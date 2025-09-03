import os

from steam_sdk.data.DataModelMagnet import DataModelMagnet


class dmm_json_schema:

    def __init__(self):
        output_file_path = os.path.join('tests', 'output_json_schema')
        data: DataModelMagnet = DataModelMagnet()

        # note that data is the Pydantic data model
        json_schema = data.schema_json()

        # oneOf works better for unions than anyOf. They fixed this in Pydantic v2.
        json_schema = json_schema.replace("anyOf", "oneOf")

        # create the JSON schema inside the current input folder
        json_schema_file_path = os.path.join(
            os.path.dirname(output_file_path), f"fiqus_schema.json"
        )
        os.makedirs(os.path.dirname(json_schema_file_path), exist_ok=True)
        with open(json_schema_file_path, "w") as file:
            file.write(json_schema)

if __name__ == "__main__":
    dmm_json_schema()
    print('21')