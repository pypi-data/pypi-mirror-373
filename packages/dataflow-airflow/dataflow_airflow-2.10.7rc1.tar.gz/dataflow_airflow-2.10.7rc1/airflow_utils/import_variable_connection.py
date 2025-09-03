import json
from dataflow import Dataflow
from airflow.providers.amazon.aws.secrets.secrets_manager import SecretsManagerBackend

class AirflowConnectionsAndVariableImport(SecretsManagerBackend):
    """
    Airflow custom secrets backend class.
    Thin wrapper around Dataflow core methods to retrieve connections and variable_or_secret.

    Attributes:
        client: The Boto3 client for Secrets Manager.
    """
    def __init__(self, **kwargs):
        super().__init__()
        self.dataflow = Dataflow()

    def get_conn_value(self, conn_id):
        """
        Get serialized representation of Connection.

        :param conn_id: connection id
        """
        try:
            connection_dict = self.dataflow.connection(conn_id, mode="dict")
            if connection_dict is None:
                raise Exception(f"Connection {conn_id} not found.")
            
            connection_dict['schema'] = connection_dict.pop('schemas', None)
            connection_dict.pop('conn_id')
            if connection_dict['conn_type'].lower() == "postgresql":
                connection_dict['conn_type'] = "postgres"
            standardized_connection_dict = self._standardize_secret_keys(connection_dict)
            if self.are_secret_values_urlencoded:
                standardized_connection_dict = self._remove_escaping_in_secret_dict(standardized_connection_dict)
            standardized_connection = json.dumps(standardized_connection_dict)
            return standardized_connection
            
        except Exception as e:
            raise Exception(f"Error retrieving connection: {e}")

    def get_variable(self, key):
        """
        Get Airflow Variable.

        :param key: Variable Key
        :return: Variable Value
        """
        try:
            variable_or_secret = self.dataflow.variable_or_secret(key)
            if variable_or_secret is None:
                raise Exception(f"Variable {key} not found.")
            
            return variable_or_secret

        except Exception as e:
            raise Exception(f"Error retrieving variable: {e}")