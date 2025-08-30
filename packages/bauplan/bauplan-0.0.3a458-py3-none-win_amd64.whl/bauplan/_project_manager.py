from __future__ import annotations

import io
import re
import zipfile
from base64 import b64encode
from pathlib import Path
from typing import Annotated, Any, Dict, Generic, List, Literal, Optional, Tuple, TypeVar, Union

import yaml
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from pydantic import BaseModel, ConfigDict, Discriminator, Field, Tag, field_validator

from ._common import Constants
from .errors import (
    ParameterMissingRequiredValuesError,
    ParameterUnexpectedKeysError,
    ParameterValueTypeError,
    ProjectDirectoryError,
    ProjectFileError,
    ProjectYamlMapperError,
    ProjectYamlParsingError,
    SecretParameterEncryptionError,
    VaultParameterValueError,
)

T = TypeVar('T')


class BaseParameter(BaseModel, Generic[T]):
    """Internal abstract representation of a parameter"""

    model_config = ConfigDict(strict=True)

    default: Optional[T] = None
    description: Optional[str] = None
    required: Optional[bool] = None

    @classmethod
    def get_type(cls) -> str:
        # Parse the object annotations to get the type (as a string)
        type_ = str(cls.__annotations__['type'])
        match = re.match(r".*Literal\['([^']+)'.*", type_)
        if match is None:
            raise ValueError(f'Invalid type annotation: {type_}')
        return match.group(1)

    @classmethod
    def to_default(
        cls,
        name: str,
        value: Optional[T],
        project_id: str,
        secret_key: Optional[str],
        secret_public_key: Optional[str],
    ) -> Optional[T]:
        # Cast/map the default value into the actual value
        return value


class BoolParameter(BaseParameter[bool]):
    type: Literal['bool', None] = None


class IntParameter(BaseParameter[int]):
    type: Literal['int', None] = None


class FloatParameter(BaseParameter[float]):
    type: Literal['float', None] = None


class StrParameter(BaseParameter[str]):
    type: Literal['str', None] = None


class VaultParameter(BaseParameter[str]):
    type: Literal['vault']

    @field_validator('default', mode='after')
    @classmethod
    def validate_default(cls, value: Optional[str]) -> Optional[str]:
        """
        Custom validator to ensure the default value is a valid vault uri

        """
        if value is None:
            return None

        # Vault values must be a valid uri
        uri = value.strip()
        if uri == '':
            raise VaultParameterValueError('expected a non-empty string')

        regex = re.compile(r'^([a-zA-Z0-9][a-zA-Z0-9-+]+)://(.+)$')
        matches = regex.match(uri)
        if not matches:
            raise VaultParameterValueError(f'expected a valid uri, got "{value}"')

        protocol = matches.group(1).strip()
        if protocol == '':
            raise VaultParameterValueError(f'vault protocol cannot be an empty string, got "{value}"')

        vault_key = matches.group(2).strip()
        if vault_key == '':
            raise VaultParameterValueError('vault key cannot be empty')

        return f'{protocol}://{vault_key}'


class SecretParameter(BaseParameter[str]):
    type: Literal['secret']
    key: Optional[str] = None

    @classmethod
    def to_default(
        cls,
        name: str,
        value: Optional[str],
        project_id: Optional[str],
        secret_key: Optional[str],
        secret_public_key: Optional[str],
    ) -> Optional[str]:
        """
        Secrets are a special case, they must be encrypted before being stored.
        """
        if value is None:
            return None
        if not isinstance(value, str):
            raise SecretParameterEncryptionError(name, 'parameter value must be a string')

        if secret_key is None:
            raise SecretParameterEncryptionError(name, 'secret key not defined, cannot encrypt the parameter')

        if secret_key.strip() == '':
            raise SecretParameterEncryptionError(name, 'secret key cannot be an empty string')

        if secret_public_key is None:
            raise SecretParameterEncryptionError(name, 'public key not defined, cannot encrypt the parameter')

        public_key = secret_public_key.strip()
        if public_key == '':
            raise SecretParameterEncryptionError(name, 'public key cannot be an empty string')

        if project_id is None:
            raise SecretParameterEncryptionError(name, 'project.id not defined, cannot encrypt the parameter')
        project_id = project_id.strip()
        if project_id == '':
            raise SecretParameterEncryptionError(name, 'project.id cannot be an empty string')

        pem = serialization.load_pem_public_key(public_key.encode())
        try:
            encrypted_value = b64encode(
                pem.encrypt(
                    # The secret value has the project_id as a prefix
                    f'{project_id}={value}'.encode(),
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None,
                    ),
                )
            )
        except Exception as e:
            raise SecretParameterEncryptionError(name, 'failed to encrypt the secret parameter') from e

        return encrypted_value.decode('ascii')


def _resolve_parameter_type(v: Any) -> str:
    """
    Helper function used by pydantic to resolve the type of a parameter

    """
    param_type = v.get('type', None) if isinstance(v, dict) else getattr(v, 'type', None)
    if isinstance(param_type, str):
        return param_type
    # Otherwise, infer the type from the default value
    default_value = v.get('default', None) if isinstance(v, dict) else getattr(v, 'default', None)
    match default_value:
        case bool():
            return BoolParameter.get_type()
        case int():
            return IntParameter.get_type()
        case float():
            return FloatParameter.get_type()
        case _:
            return StrParameter.get_type()


ParameterTypes = Annotated[
    Union[
        Annotated['BoolParameter', Tag(BoolParameter.get_type())],
        Annotated['IntParameter', Tag(IntParameter.get_type())],
        Annotated['FloatParameter', Tag(FloatParameter.get_type())],
        Annotated['StrParameter', Tag(StrParameter.get_type())],
        Annotated['VaultParameter', Tag(VaultParameter.get_type())],
        Annotated['SecretParameter', Tag(SecretParameter.get_type())],
    ],
    Discriminator(_resolve_parameter_type),
]


class Project(BaseModel):
    id: str = ''
    name: Optional[str] = None
    description: Optional[str] = None

    @field_validator('id', mode='before')
    @classmethod
    def validate_id(cls, v: Optional[str]) -> str:
        if not isinstance(v, str):
            raise ValueError('project.id must be a string')
        match len(v):
            case 0:
                raise ValueError('project.id cannot be an empty string')
            case _:
                return v.strip()


class ProjectManager(BaseModel):
    file_path: Optional[Path] = Field(default=None, repr=False, exclude=True)

    project: Project = Field(default_factory=Project)
    parameters: Dict[str, ParameterTypes] = Field(default_factory=dict)

    @property
    def dir_path(self) -> Path:
        assert self.file_path is not None
        return self.file_path.parent

    def overwrite_secret_parameters(
        self,
        overwrite_values: Dict[str, Optional[Union[str, int, float, bool]]],
    ) -> bool:
        # Check if the user wants to overwrite any secret parameters
        for k, v in overwrite_values.items():
            param = self.parameters.get(k, None)
            if isinstance(param, SecretParameter) and v is not None:
                return True
        return False

    def resolve_parameters(
        self,
        overwrite_values: Dict[str, Optional[Union[str, int, float, bool]]],
        secret_key: Optional[str] = None,
        secret_public_key: Optional[str] = None,
    ) -> Tuple[Dict[str, BaseParameter], Dict[str, Optional[Union[str, int, float, bool]]]]:
        parameters: Dict[str, BaseParameter] = {}
        raw_values: Dict[str, Any] = {}
        missing_required_params: set[str] = set()

        unknown_params = set(overwrite_values.keys()) - set(self.parameters.keys())
        if len(unknown_params) > 0:
            raise ParameterUnexpectedKeysError(unknown_params)

        for name, param in self.parameters.items():
            if name in overwrite_values:
                # The user wants to override the default value
                new_default = param.to_default(
                    name=name,
                    value=overwrite_values[name],  # type: ignore
                    project_id=self.project.id,
                    secret_key=secret_key,
                    secret_public_key=secret_public_key,
                )
                try:
                    parameters[name] = param.__class__(**{
                        **param.model_dump(mode='python'),
                        'default': new_default,
                        'key': secret_key,
                    })
                    raw_values[name] = new_default
                except ValueError as e:
                    raise ParameterValueTypeError(name, overwrite_values[name], param.get_type()) from e
            else:
                parameters[name] = param.model_copy(deep=True)
                raw_values[name] = param.default

            if param.required is True and parameters[name].default is None:
                missing_required_params.add(name)

        if len(missing_required_params) > 0:
            raise ParameterMissingRequiredValuesError(missing_required_params)

        return parameters, raw_values

    def package(
        self,
        overwrite_values: Dict[str, Optional[Union[str, int, float, bool]]],
        secret_key: Optional[str] = None,
        secret_public_key: Optional[str] = None,
    ) -> Tuple[bytes, Dict[str, BaseParameter], Dict[str, Any]]:
        """
        Convert the project into a package
        """
        assert self.dir_path, 'Can not package project without a file path'

        parameters, raw_values = self.resolve_parameters(
            overwrite_values=overwrite_values,
            secret_key=secret_key,
            secret_public_key=secret_public_key,
        )
        pack = SnapshotPackager(project_manager=self)
        return pack.package(), parameters, raw_values

    @classmethod
    def parse_project_dir(cls, project_dir: Path | str) -> ProjectManager:
        project_path = cls._ensure_project_dir(project_dir)

        # Check if both files exist
        yml_path = project_path / f'{Constants.PROJECT_FILE_NAME}.yml'
        yml_exists = yml_path.exists()

        yaml_path = project_path / f'{Constants.PROJECT_FILE_NAME}.yaml'
        yaml_exists = yaml_path.exists()

        # Error if neither file exists
        if not yml_exists and not yaml_exists:
            raise ProjectFileError(
                project_path,
                f'Neither {Constants.PROJECT_FILE_NAME}.yml nor {Constants.PROJECT_FILE_NAME}.yaml files found in the project directory',
            )

        # Error if both files exist
        if yml_exists and yaml_exists:
            raise ProjectFileError(
                project_path,
                f'Both {Constants.PROJECT_FILE_NAME}.yml and {Constants.PROJECT_FILE_NAME}.yaml files found in the project directory. Please remove one to avoid ambiguity',
            )

        return cls.parse_yaml_file(yml_path if yml_exists else yaml_path)

    @classmethod
    def parse_yaml_file(cls, file_path: Path | str) -> ProjectManager:
        file_path = cls._ensure_project_file(file_path)
        try:
            project_config = yaml.safe_load(file_path.read_text())
            assert isinstance(project_config, dict), 'Invalid yaml file'
        except Exception as e:
            raise ProjectYamlParsingError(file_path, e) from e

        obj = cls(**project_config, file_path=file_path)

        if obj.project.id.strip() == '':
            raise ProjectYamlMapperError(file_path, 'project.id cannot be an empty string')

        return obj

    @staticmethod
    def _ensure_project_dir(project_dir: Optional[Union[Path, str]]) -> Path:
        assert project_dir, 'project_dir is required'
        project_path = Path(project_dir).expanduser().resolve()
        if not project_path.exists():
            raise ProjectDirectoryError(project_path, f'{project_path} directory does not exist')
        if not project_path.is_dir():
            raise ProjectDirectoryError(project_path, f'{project_path} is not a directory')
        return project_path

    @staticmethod
    def _ensure_project_file(file_path: Optional[Union[Path, str]]) -> Path:
        assert file_path, 'file_path is required'
        file_path = Path(file_path).expanduser().resolve()
        if not file_path.exists():
            raise ProjectFileError(file_path, f'{file_path} file does not exist')
        if not file_path.is_file():
            raise ProjectFileError(file_path, f'{file_path} is not a file')
        return file_path


class SnapshotPackager(BaseModel):
    project_manager: ProjectManager
    included_files: List[str] = Field(default_factory=list)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.project_manager._ensure_project_file(self.project_manager.file_path)

    def package(self) -> bytes:
        assert self.project_manager.file_path is not None

        self.included_files = []

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in self._get_supported_files(self.project_manager.dir_path):
                abs_path = file_path.relative_to(self.project_manager.dir_path)
                self.included_files.append(str(abs_path))
                zf.write(file_path, abs_path)

        return zip_buffer.getvalue()

    def _get_supported_files(self, project_dir: Path) -> List[Path]:
        return [file_path for file_path in project_dir.iterdir() if self._can_include(project_dir, file_path)]

    def _can_include(self, project_dir: Path, file_path: Path) -> bool:
        if not file_path.is_file():
            return False

        rel_path = file_path.relative_to(project_dir)
        if len(rel_path.parts) == 1:
            # We don't support subdirectories
            if rel_path.suffix.lower().endswith(('.py', '.sql')):
                return True
            if str(rel_path) == 'requirements.txt':
                return True
            if str(rel_path) == f'{Constants.PROJECT_FILE_NAME}.yml':
                return True
            if str(rel_path) == f'{Constants.PROJECT_FILE_NAME}.yaml':
                return True

        return False
