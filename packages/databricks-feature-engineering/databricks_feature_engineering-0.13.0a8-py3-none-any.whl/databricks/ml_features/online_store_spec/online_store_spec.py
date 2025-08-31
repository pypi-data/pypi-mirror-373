import abc
import copy
import logging
from typing import Dict, List, Union

from databricks.ml_features.online_store_spec.online_store_properties import (
    DATABASE_NAME,
    DRIVER_NAME,
    EXPLICIT_CREDENTIAL_PARAMS,
    HOSTNAME,
    PASSWORD,
    PORT,
    READ_SECRET_PREFIX,
    TABLE_NAME,
    TYPE,
    USER,
    WRITE_SECRET_PREFIX,
)
from databricks.ml_features.utils.utils import _get_dbutils as get_dbutils
from databricks.ml_features.utils.utils import is_empty
from databricks.ml_features_common.utils.uc_utils import LOCAL_METASTORE_NAMES
from databricks.ml_features_common.utils.utils_common import deprecated

_logger = logging.getLogger(__name__)


class OnlineStoreSpec(abc.ABC):
    """
    .. note::

       Aliases: `!databricks.feature_engineering.online_store_spec.OnlineStoreSpec`, `!databricks.feature_store.online_store_spec.OnlineStoreSpec`

    Parent class for all types of :class:`OnlineStoreSpec` objects.

    Abstract base class for classes that specify the online store to publish to.

    If `database_name` and `table_name` are not provided,
    :meth:`publish_table() <databricks.feature_engineering.client.FeatureEngineeringClient.publish_table>`
    will use the offline store's database and table
    names.

    To use a different database and table name in the online store, provide values for
    both `database_name` and `table_name` arguments.

    The JDBC driver can be customized with the optional ``driver_name`` argument.
    Otherwise, a default is used.

    Strings in the primary key should not exceed 100 characters.

    The online database should already exist.

    .. note::

       It is strongly suggested (but not required), to provide read-only database credentials via
       the ``read_secret_prefix`` in order to grant the least amount of database access
       privileges to the served model.  When providing a ``read_secret_prefix``, the secrets must
       exist in the scope name using the expected format,
       otherwise :meth:`publish_table() <databricks.feature_engineering.client.FeatureEngineeringClient.publish_table>` will return an error.

    :param hostname: Hostname to access online store. The database hostname cannot be changed. Subsequent publish
      calls to the same online store must provide the same hostname.
    :param port: Port number to access online store. The database port cannot be changed. Subsequent publish
      calls to the same online store must provide the same port.
    :param user: Username that has write access to the online store. **Deprecated**. Use ``write_secret_prefix`` instead.

    :param password: Password to access the online store. **Deprecated**. Use ``write_secret_prefix`` instead.

    :param database_name: Database name.
    :param table_name: Table name.
    :param driver_name: Name of custom JDBC driver to access the online store.
    :param read_secret_prefix: The secret scope name and secret key name prefix where read-only online store
      credentials are stored. These credentials will be used during online feature serving to connect to the
      online store from the served model. The format of this parameter should be ``${scope-name}/${prefix}``,
      which is the name of the secret scope, followed by a ``/``, followed by the secret key name prefix. The
      scope passed in must contain the following keys and corresponding values:

      * ``${prefix}-user`` where ``${prefix}`` is the value passed into this function. For example if this
        function is called with ``datascience/staging``, the ``datascience`` secret scope should contain the
        secret named ``staging-user``, which points to a secret value with the database username for the
        online store.

      * ``${prefix}-password`` where ``${prefix}`` is the value passed into this function. For example if this
        function is called with ``datascience/staging``, the ``datascience`` secret scope should contain the
        secret named ``staging-password``, which points to a secret value with the database password for the
        online store.

      Once the read_secret_prefix is set for an online store, it cannot be changed.

    :param write_secret_prefix: The secret scope name and secret key name prefix where read-write online store
      credentials are stored. These credentials will be used to connect to the online store to publish
      features. If ``user`` and ``password`` are passed, this field must be ``None``, or an exception will be raised.
      The format of this parameter should be ``${scope-name}/${prefix}``, which is the name of the secret scope,
      followed by a ``/``, followed by the secret key name prefix. The scope passed in must contain the following
      keys and corresponding values:

      * ``${prefix}-user`` where ``${prefix}`` is the value passed into this function.  For example if this
        function is called with ``datascience/staging``, the ``datascience`` secret scope should contain the
        secret named ``staging-user``, which points to a secret value with the database username for the
        online store.

      * ``${prefix}-password`` where ``${prefix}`` is the value passed into this function.  For example if this
        function is called with ``datascience/staging``, the ``datascience`` secret scope should contain the
        secret named ``staging-password``, which points to a secret value with the database password for the
        online store.

    """

    # TODO (ML-23105): Remove explicit parameters for MLR 12.0.
    @abc.abstractmethod
    def __init__(
        self,
        _type,
        hostname: [str, None] = None,
        port: [int, None] = None,
        user: Union[str, None] = None,
        password: Union[str, None] = None,
        database_name: Union[str, None] = None,
        table_name: Union[str, None] = None,
        driver_name: Union[str, None] = None,
        read_secret_prefix: Union[str, None] = None,
        write_secret_prefix: Union[str, None] = None,
        _internal_properties: Union[Dict[str, str], None] = None,
    ):
        self._properties = {
            TYPE: _type,
            HOSTNAME: hostname,
            PORT: port,
            DATABASE_NAME: database_name,
            TABLE_NAME: table_name,
            USER: user,
            PASSWORD: password,
            DRIVER_NAME: driver_name,
            READ_SECRET_PREFIX: read_secret_prefix,
            WRITE_SECRET_PREFIX: write_secret_prefix,
        }
        if _internal_properties:
            self._properties.update(_internal_properties)
        self._validate_credentials()
        self._warn_on_explicit_credentials()

    def _validate_credentials(self):
        """
        Validate that the expected credentials were provided and are unambiguous.
        Subclasses with different behavior should override this.
        """
        # Validate that the user passed either a user/pass combination or a write_secret_prefix, else throw an error
        # because otherwise there are no database credentials to use
        # TODO (ML-19653): Align the allowed credentials and error messages
        if self.write_secret_prefix is None and (
            self._properties[USER] is None or self._properties[PASSWORD] is None
        ):
            raise Exception(
                "Use either 'user'/'password' combination or 'write_secret_prefix'."
            )

        # Validate that user didn't pass user/pass AND write_secret_prefix, or else throw an error because this
        # is ambiguous
        if (
            not is_empty(self._properties[USER])
            and self.write_secret_prefix is not None
        ):
            raise Exception("Use either 'user' or 'write_secret_prefix', but not both.")
        if (
            not is_empty(self._properties[PASSWORD])
            and self.write_secret_prefix is not None
        ):
            raise Exception(
                "Use either 'password' or 'write_secret_prefix', but not both."
            )

    def _warn_on_explicit_credentials(self):
        """
        Warn if any explicit credential parameters are used as they are deprecated.
        """
        explicit_credentials = [
            f'"{p}"'
            for p in EXPLICIT_CREDENTIAL_PARAMS
            if self._properties.get(p, None)
        ]
        if explicit_credentials:
            # Parameters use underscore "_". while secrets and the internal constants use dash "-"
            params_str = ", ".join(explicit_credentials).replace("-", "_")
            _logger.warning(
                f'The explicit credential parameters {params_str} is deprecated. Use "write_secret_prefix" instead.'
            )

    @property
    def type(self):
        """Type of the online store."""
        return self._properties[TYPE]

    @property
    def table_name(self):
        """Table name."""
        return self._properties[TABLE_NAME]

    @property
    @deprecated(alternative="write_secret_prefix")
    def user(self):
        """Username that has access to the online store.

        Property will be empty if ``write_secret_prefix`` argument was used.
        """
        return self._properties[USER]

    @property
    @deprecated(alternative="write_secret_prefix")
    def password(self):
        """Password to access the online store.

        Property will be empty if ``write_secret_prefix`` argument was used.
        """
        return self._properties[PASSWORD]

    @property
    def driver(self):
        """Name of the custom JDBC driver to access the online store."""
        return self._properties[DRIVER_NAME]

    @property
    def read_secret_prefix(self):
        """
        Prefix for read access to online store.

        Name of the secret scope and prefix that contains the username and password to access
        the online store with read-only credentials.

        See the ``read_secret_prefix`` parameter description for details.
        """
        return self._properties[READ_SECRET_PREFIX]

    @property
    def write_secret_prefix(self):
        """
        Secret prefix that contains online store login info.

        Name of the secret scope and prefix that contains the username and password to access
        the online store with read/write credentials.
        See the ``write_secret_prefix`` parameter description for details.
        """
        return self._properties[WRITE_SECRET_PREFIX]

    @property
    def cloud(self):
        """Cloud provider where this online store is located."""
        raise NotImplementedError

    @property
    def store_type(self):
        """Store type."""
        raise NotImplementedError

    @property
    def _jdbc_parameters(self) -> str:
        """
        List of parameters to include in the JDBC URL.
        """
        return ""

    def auth_type(self):
        """Publish Auth type."""
        raise NotImplementedError

    def clone(self, **kwargs):
        """Clone a feature spec."""
        new_spec = copy.deepcopy(self)
        new_spec._properties.update(kwargs)
        return new_spec

    def non_secret_properties(self):
        """
        TODO (ML-21692): Determine if this function is required and update for use if necessary.

        Dictionary of non-secret properties.
        """
        keys = [
            TYPE,
            HOSTNAME,
            PORT,
            DATABASE_NAME,
            TABLE_NAME,
        ]
        return {key: self._properties[key] for key in keys}

    def _lookup_user_with_write_permissions(self) -> str:
        """
        Username that has write access to the online store, based on either being provided directly via the constructor
        or by resolving via write_secret_prefix and dbutils.

        This contains only the username as stored in the secret.  If you need the authorization user for the
        purposes of putting into a jdbc connection string, which may contain more than just the username,
        call _lookup_jdbc_auth_user_with_write_permissions() instead.

        WARNING: do not hold onto the returned secret for longer than necessary, for example saving in
        data structures, files, other persistent backends.  Use it only for directly accessing resources
        and then allow the Python VM to remove the reference as soon as it's out of scope.
        """
        return self._lookup_secret_with_write_permissions(USER)

    def _lookup_password_with_write_permissions(self) -> str:
        """
        Password that has write access to the online store, based on either being provided directly via the constructor
        or by resolving via write_secret_prefix and dbutils.

        WARNING: do not hold onto the returned secret for longer than necessary, for example saving in
        data structures, files, other persistent backends.  Use it only for directly accessing resources
        and then allow the Python VM to remove the reference as soon as it's out of scope.
        """
        return self._lookup_secret_with_write_permissions(PASSWORD)

    def _valid_secret_suffixes(self) -> List[str]:
        """
        List of valid secret suffixes.
        Defaults to "user" and "password," but subclasses with different behavior should override this.
        """
        return [USER, PASSWORD]

    def _expected_secret_suffixes(self) -> List[str]:
        """
        List of expected secret suffixes.
        Defaults to "user" and "password," but subclasses with different behavior should override this.
        """
        return [USER, PASSWORD]

    def _lookup_secret_with_write_permissions(self, secret) -> str:
        """
        Lookup secret (either user or password) that has write permissions to the online store.

        WARNING: do not hold onto the returned secrets for longer than necessary, for example saving in
        data structures, files, other persistent backends.  Use it only for directly accessing resources
        and then allow the VM to clean up the variable in memory.
        """

        # Ensure a valid secret was passed
        if secret not in self._valid_secret_suffixes():
            raise Exception("Internal error: invalid secret passed")

        # Validate the read_secret_prefix to catch missing secrets as early as possible.
        # TODO (ML-21737): Determine if this validation should be done earlier.
        self._validate_read_secrets()

        # If the user passed in the secret directly via the constructor rather than via WRITE_SECRET_PREFIX, return it
        if not is_empty(self._properties.get(secret)):
            return self._properties[secret]

        # Otherwise the user must have passed the secret via WRITE_SECRET_PREFIX, so resolve the secret and return it
        return self._lookup_write_secret_for_suffix(secret)

    def _lookup_jdbc_auth_user_with_write_permissions(self) -> str:
        """
        Generate the user authentication string used in the JDBC URL.  The default behavior is "user", but subclasses
        should override this if the particular online store requires customization.  For example, on AzureMysql
        it requires the format: "user@server"
        """
        return self._lookup_user_with_write_permissions()

    def _lookup_write_secret_for_suffix(self, suffix) -> Union[str, None]:
        """
        Resolve and validate the secrets referenced in the write_secret_prefix via dbutils for the given suffix.
        Valid suffix values depend on the online store, and are defined by `_valid_secret_prefixes`.

        This must happen during the construction of the jdbc url rather than during construction of the OnlineStoreSpec object
        because the user may modify the underlying secrets being pointed to by WRITE_SECRET_PREFIX, and we need to
        validate the latest secret values rather than a snapshot of the values at the time OnlineStoreSpec was created.

        WARNING: do not hold onto the returned secrets for longer than necessary, for example saving in
        data structures, files, other persistent backends.  Use it only for directly accessing resources
        and then allow the VM to clean up the variable in memory.

        Returns the secret corresponding to either the user or password, depending on the given suffix.
        """

        # If write_secret_prefix is None, there is nothing to do
        if self._properties[WRITE_SECRET_PREFIX] is None:
            return None

        # Ensure a valid suffix was passed
        if suffix not in self._valid_secret_suffixes():
            raise Exception("Internal error: invalid suffix passed")

        # Get a reference to dbutils, which only works within a notebook or notebook job context
        dbutils = get_dbutils()

        # Use dbutils to lookup write_scope_secrets and return to the caller.  Propagate the exception if either
        # the scope or either secret does not exist in the secret store.
        write_creds_scope, write_creds_prefix = _parse_scope_prefix(
            self._properties[WRITE_SECRET_PREFIX]
        )
        return dbutils.secrets.get(
            scope=write_creds_scope,
            key=f"{write_creds_prefix}-{suffix}",
        )

    def _validate_read_secrets(self):
        """
        Validate that the READ_SECRET_PREFIX contains a valid scope with the expected secrets.
        """

        # If read_secret_prefix is None, there is nothing to do
        if self._properties[READ_SECRET_PREFIX] is None:
            return

        # Get a reference to dbutils, which only works within a notebook or notebook job context
        dbutils = get_dbutils()

        # Use dbutils to lookup read_scope_secrets and store in properties, or throw an error if the scope or secrets
        # do not exist.  The actual secrets are discarded since the lookup is performed only for validation purposes.
        read_creds_scope, read_creds_prefix = _parse_scope_prefix(
            self._properties[READ_SECRET_PREFIX]
        )
        # Check all the expected suffixes are present in the read secrets
        for secret_suffix in self._expected_secret_suffixes():
            dbutils.secrets.get(
                scope=read_creds_scope,
                key=f"{read_creds_prefix}-{secret_suffix}",
            )

    def _augment_online_store_spec(self, full_feature_table_name):
        """
        Apply default values for member variables of online_store that are None.
        """
        raise NotImplementedError

    def _augment_sql_online_store_spec_helper(
        self, full_feature_table_name, database_name, table_name
    ):
        """
        Apply default database and table name for SQL databases.
        Local workspace hive metastore: database = <database>, table = <table>
        UC: database = <catalog>-<database>, table = <table>
        """
        if (database_name is None) != (table_name is None):
            raise ValueError(
                f"The OnlineStoreSpec {self.store_type} must specify either both database_name "
                f"and table_name, or neither."
            )
        elif (database_name is None) and (table_name is None):
            catalog_name, database_name, table_name = full_feature_table_name.split(".")
            online_database_name = (
                f"{database_name}"
                if catalog_name in LOCAL_METASTORE_NAMES
                else f"{catalog_name}-{database_name}"
            )
            return self.clone(
                **{DATABASE_NAME: online_database_name, TABLE_NAME: table_name}
            )
        return self

    def _get_online_store_name(self):
        """
        Derives and returns the online store name based on the provided online store type.
        Assumes that the online store spec is well formed (e.g. augmented with the relevant database/table names)
        """
        raise NotImplementedError


def _parse_scope_prefix(scope_prefix):
    """
    Parse the secret scope + prefix into its components and do validation.

    foo/bar -> ["foo", "bar"]
    """

    format_message = (
        "The format of this parameter should be ${scope}/${prefix}, which is the name of the "
        "secret scope, followed by a /, followed by a user-defined prefix that is used to "
        "determine the secret key to be used."
    )

    if scope_prefix is None or len(scope_prefix) == 0:
        raise Exception(format_message)

    if "/" not in scope_prefix:
        raise Exception(format_message)

    split_vals = scope_prefix.split("/")

    if len(split_vals) != 2:
        raise Exception(format_message)

    return split_vals
