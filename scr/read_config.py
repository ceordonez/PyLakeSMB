import yaml

def read_config():
    with open('config_model.yml', 'r') as file:
        conf_model = yaml.safe_load(file)
    with open('data_lake.yml', 'r') as file:
        conf_lake = yaml.safe_load(file)
    return conf_model, conf_lake
