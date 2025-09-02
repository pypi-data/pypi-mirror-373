[
  {
    "oid": "test_pg_gen_0cca28df-03d1-4e60-9422-d4ff985e5e57_0",
    "name": "Python App",
    "categoryType": "Application",
    "category": "PythonApp",
    "dropclass": "dlg.apps.simple.HelloWorldApp",
    "storage": "PythonApp",
    "rank": [
      0
    ],
    "reprodata": {},
    "loop_ctx": null,
    "weight": 5,
    "num_cpus": 1,
    "applicationArgs": {
      "hello": {
        "defaultValue": "",
        "description": " The port carrying the message produced by the app.",
        "encoding": "pickle",
        "id": "b845e9f8-d19c-4fc7-a073-8bcc64e086e2",
        "name": "hello",
        "options": [],
        "parameterType": "ApplicationArgument",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "OutputPort",
        "value": ""
      }
    },
    "constraintParams": {
      "execution_time": {
        "defaultValue": "5",
        "description": "Estimate of execution time (in seconds) for this application.",
        "encoding": "pickle",
        "id": "f720235d-fdf3-4787-b481-f833415e4e71",
        "name": "execution_time",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Float",
        "usage": "NoPort",
        "value": 5
      },
      "num_cpus": {
        "defaultValue": "1",
        "description": "Number of CPUs used for this application.",
        "encoding": "pickle",
        "id": "e2e5a85a-b0a1-4393-b8fa-f3e468f5c082",
        "name": "num_cpus",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Integer",
        "usage": "NoPort",
        "value": 1
      }
    },
    "componentParams": {
      "group_start": {
        "defaultValue": "false",
        "description": "Is this node the start of a group?",
        "encoding": "pickle",
        "id": "dc6d96ad-2afd-44c5-85f2-55d18468db74",
        "name": "group_start",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Boolean",
        "usage": "NoPort",
        "value": false
      },
      "dropclass": {
        "defaultValue": "test.graphsRepository",
        "description": "The python class that implements this application",
        "encoding": "pickle",
        "id": "acf2f5ed-9219-45a5-8e91-216e8bedd155",
        "name": "dropclass",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "NoPort",
        "value": "dlg.apps.simple.HelloWorldApp"
      }
    },
    "fields": [
      {
        "defaultValue": "5",
        "description": "Estimate of execution time (in seconds) for this application.",
        "encoding": "pickle",
        "id": "f720235d-fdf3-4787-b481-f833415e4e71",
        "name": "execution_time",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Float",
        "usage": "NoPort",
        "value": 5
      },
      {
        "defaultValue": "1",
        "description": "Number of CPUs used for this application.",
        "encoding": "pickle",
        "id": "e2e5a85a-b0a1-4393-b8fa-f3e468f5c082",
        "name": "num_cpus",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Integer",
        "usage": "NoPort",
        "value": 1
      },
      {
        "defaultValue": "false",
        "description": "Is this node the start of a group?",
        "encoding": "pickle",
        "id": "dc6d96ad-2afd-44c5-85f2-55d18468db74",
        "name": "group_start",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Boolean",
        "usage": "NoPort",
        "value": false
      },
      {
        "defaultValue": "test.graphsRepository",
        "description": "The python class that implements this application",
        "encoding": "pickle",
        "id": "acf2f5ed-9219-45a5-8e91-216e8bedd155",
        "name": "dropclass",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "NoPort",
        "value": "dlg.apps.simple.HelloWorldApp"
      },
      {
        "defaultValue": "",
        "description": " The port carrying the message produced by the app.",
        "encoding": "pickle",
        "id": "b845e9f8-d19c-4fc7-a073-8bcc64e086e2",
        "name": "hello",
        "options": [],
        "parameterType": "ApplicationArgument",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "OutputPort",
        "value": ""
      }
    ],
    "execution_time": 5,
    "group_start": false,
    "hello": "",
    "iid": "0",
    "lg_key": "0cca28df-03d1-4e60-9422-d4ff985e5e57",
    "outputs": [
      {
        "test_pg_gen_cd274ac6-7e66-4216-adc2-a13799ea46da_0": "hello"
      }
    ],
    "node": "10.128.0.12",
    "island": "10.128.0.11",
    "humanReadableKey": "1_0"
  },
  {
    "oid": "test_pg_gen_cd274ac6-7e66-4216-adc2-a13799ea46da_0",
    "name": "Shared Memory",
    "categoryType": "Data",
    "category": "SharedMemory",
    "dropclass": "dlg.data.drops.memory.SharedMemoryDROP",
    "storage": "SharedMemory",
    "rank": [
      0
    ],
    "reprodata": {},
    "loop_ctx": null,
    "weight": 5,
    "applicationArgs": {
      "hello": {
        "defaultValue": "",
        "description": " The port carrying the message produced by the app.",
        "encoding": "pickle",
        "id": "a8ecb5d5-55d3-4d2e-80d4-7f019afdf179",
        "name": "hello",
        "options": [],
        "parameterType": "ApplicationArgument",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "InputPort",
        "value": ""
      },
      "data": {
        "defaultValue": "",
        "description": "",
        "encoding": "pickle",
        "id": "7c3bdeac-cb1d-4502-9ada-d7fc65344200",
        "name": "data",
        "options": [],
        "parameterType": "ApplicationArgument",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "OutputPort",
        "value": ""
      }
    },
    "constraintParams": {
      "data_volume": {
        "defaultValue": "5",
        "description": "Estimated size of the data contained in this node",
        "encoding": "pickle",
        "id": "c8468235-acd4-498f-9eda-c5e6f4f0cad7",
        "name": "data_volume",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Float",
        "usage": "NoPort",
        "value": 5
      }
    },
    "componentParams": {
      "group_end": {
        "defaultValue": "false",
        "description": "Is this node the end of a group?",
        "encoding": "pickle",
        "id": "ee13b53b-891d-48c0-b8ba-7fe1a13e5cf7",
        "name": "group_end",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Boolean",
        "usage": "NoPort",
        "value": false
      },
      "dropclass": {
        "defaultValue": "dlg.data.drops.memory.SharedMemoryDROP",
        "description": "",
        "encoding": "pickle",
        "id": "e5a30ddc-840b-4374-8a6c-601c21917a22",
        "name": "dropclass",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "NoPort",
        "value": "dlg.data.drops.memory.SharedMemoryDROP"
      }
    },
    "fields": [
      {
        "defaultValue": "5",
        "description": "Estimated size of the data contained in this node",
        "encoding": "pickle",
        "id": "c8468235-acd4-498f-9eda-c5e6f4f0cad7",
        "name": "data_volume",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Float",
        "usage": "NoPort",
        "value": 5
      },
      {
        "defaultValue": "false",
        "description": "Is this node the end of a group?",
        "encoding": "pickle",
        "id": "ee13b53b-891d-48c0-b8ba-7fe1a13e5cf7",
        "name": "group_end",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Boolean",
        "usage": "NoPort",
        "value": false
      },
      {
        "defaultValue": "",
        "description": " The port carrying the message produced by the app.",
        "encoding": "pickle",
        "id": "a8ecb5d5-55d3-4d2e-80d4-7f019afdf179",
        "name": "hello",
        "options": [],
        "parameterType": "ApplicationArgument",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "InputPort",
        "value": ""
      },
      {
        "defaultValue": "",
        "description": "",
        "encoding": "pickle",
        "id": "7c3bdeac-cb1d-4502-9ada-d7fc65344200",
        "name": "data",
        "options": [],
        "parameterType": "ApplicationArgument",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "OutputPort",
        "value": ""
      },
      {
        "defaultValue": "dlg.data.drops.memory.SharedMemoryDROP",
        "description": "",
        "encoding": "pickle",
        "id": "e5a30ddc-840b-4374-8a6c-601c21917a22",
        "name": "dropclass",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "NoPort",
        "value": "dlg.data.drops.memory.SharedMemoryDROP"
      }
    ],
    "data_volume": 5,
    "group_end": false,
    "hello": "",
    "data": "",
    "iid": "0",
    "lg_key": "cd274ac6-7e66-4216-adc2-a13799ea46da",
    "producers": [
      {
        "test_pg_gen_0cca28df-03d1-4e60-9422-d4ff985e5e57_0": "hello"
      }
    ],
    "consumers": [
      {
        "test_pg_gen_6c904754-5fd8-4960-aaf6-c1af72dab142_0": "data"
      },
      {
        "test_pg_gen_9aa5cc70-c08b-4c99-9607-64e0436c12ce_0": "data"
      },
      {
        "test_pg_gen_7e01974d-2611-4358-82e7-c7ef796de0c5_0": "data"
      }
    ],
    "node": "10.128.0.12",
    "island": "10.128.0.11",
    "humanReadableKey": "2_0"
  },
  {
    "oid": "test_pg_gen_6c904754-5fd8-4960-aaf6-c1af72dab142_0",
    "name": "Python App",
    "categoryType": "Application",
    "category": "PythonApp",
    "dropclass": "dlg.apps.simple.CopyApp",
    "storage": "PythonApp",
    "rank": [
      0
    ],
    "reprodata": {},
    "loop_ctx": null,
    "weight": 5,
    "num_cpus": 1,
    "applicationArgs": {
      "data": {
        "defaultValue": "",
        "description": "",
        "encoding": "pickle",
        "id": "03b96b10-8f1a-4fec-b1d9-f6799146dd77",
        "name": "data",
        "options": [],
        "parameterType": "ApplicationArgument",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "InputOutput",
        "value": ""
      }
    },
    "constraintParams": {
      "execution_time": {
        "defaultValue": "5",
        "description": "Estimate of execution time (in seconds) for this application.",
        "encoding": "pickle",
        "id": "c8e42cde-4b97-40cf-a3f8-13054e8ae036",
        "name": "execution_time",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Float",
        "usage": "NoPort",
        "value": 5
      },
      "num_cpus": {
        "defaultValue": "1",
        "description": "Number of CPUs used for this application.",
        "encoding": "pickle",
        "id": "573aad0d-47f3-47f1-a68b-6ee3cf22cd56",
        "name": "num_cpus",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Integer",
        "usage": "NoPort",
        "value": 1
      }
    },
    "componentParams": {
      "group_start": {
        "defaultValue": "false",
        "description": "Is this node the start of a group?",
        "encoding": "pickle",
        "id": "c50b2df6-1488-4555-a81d-5908485f7f81",
        "name": "group_start",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Boolean",
        "usage": "NoPort",
        "value": false
      },
      "dropclass": {
        "defaultValue": "test.graphsRepository",
        "description": "The python class that implements this application",
        "encoding": "pickle",
        "id": "519c1c82-7581-40cb-bc1d-431c05516262",
        "name": "dropclass",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "NoPort",
        "value": "dlg.apps.simple.CopyApp"
      }
    },
    "fields": [
      {
        "defaultValue": "5",
        "description": "Estimate of execution time (in seconds) for this application.",
        "encoding": "pickle",
        "id": "c8e42cde-4b97-40cf-a3f8-13054e8ae036",
        "name": "execution_time",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Float",
        "usage": "NoPort",
        "value": 5
      },
      {
        "defaultValue": "1",
        "description": "Number of CPUs used for this application.",
        "encoding": "pickle",
        "id": "573aad0d-47f3-47f1-a68b-6ee3cf22cd56",
        "name": "num_cpus",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Integer",
        "usage": "NoPort",
        "value": 1
      },
      {
        "defaultValue": "false",
        "description": "Is this node the start of a group?",
        "encoding": "pickle",
        "id": "c50b2df6-1488-4555-a81d-5908485f7f81",
        "name": "group_start",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Boolean",
        "usage": "NoPort",
        "value": false
      },
      {
        "defaultValue": "test.graphsRepository",
        "description": "The python class that implements this application",
        "encoding": "pickle",
        "id": "519c1c82-7581-40cb-bc1d-431c05516262",
        "name": "dropclass",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "NoPort",
        "value": "dlg.apps.simple.CopyApp"
      },
      {
        "defaultValue": "",
        "description": "",
        "encoding": "pickle",
        "id": "03b96b10-8f1a-4fec-b1d9-f6799146dd77",
        "name": "data",
        "options": [],
        "parameterType": "ApplicationArgument",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "InputOutput",
        "value": ""
      }
    ],
    "execution_time": 5,
    "group_start": false,
    "data": "",
    "iid": "0",
    "lg_key": "6c904754-5fd8-4960-aaf6-c1af72dab142",
    "inputs": [
      {
        "test_pg_gen_cd274ac6-7e66-4216-adc2-a13799ea46da_0": "data"
      }
    ],
    "outputs": [
      {
        "test_pg_gen_4c44a7b5-02d0-414a-a089-0af4394486f4_0": "data"
      }
    ],
    "node": "10.128.0.12",
    "island": "10.128.0.11",
    "humanReadableKey": "3_0"
  },
  {
    "oid": "test_pg_gen_7e01974d-2611-4358-82e7-c7ef796de0c5_0",
    "name": "Python App",
    "categoryType": "Application",
    "category": "PythonApp",
    "dropclass": "dlg.apps.simple.CopyApp",
    "storage": "PythonApp",
    "rank": [
      0
    ],
    "reprodata": {},
    "loop_ctx": null,
    "weight": 5,
    "num_cpus": 1,
    "applicationArgs": {
      "data": {
        "defaultValue": "",
        "description": "",
        "encoding": "pickle",
        "id": "2b5dc75a-2588-4ef2-bf5a-b2a22b32ba23",
        "name": "data",
        "options": [],
        "parameterType": "ApplicationArgument",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "InputOutput",
        "value": ""
      }
    },
    "constraintParams": {
      "execution_time": {
        "defaultValue": "5",
        "description": "Estimate of execution time (in seconds) for this application.",
        "encoding": "pickle",
        "id": "1eea1f1f-674d-4f20-aabc-fb7c09a3c55b",
        "name": "execution_time",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Float",
        "usage": "NoPort",
        "value": 5
      },
      "num_cpus": {
        "defaultValue": "1",
        "description": "Number of CPUs used for this application.",
        "encoding": "pickle",
        "id": "4143a443-ae13-4096-a547-278f8a333908",
        "name": "num_cpus",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Integer",
        "usage": "NoPort",
        "value": 1
      }
    },
    "componentParams": {
      "group_start": {
        "defaultValue": "false",
        "description": "Is this node the start of a group?",
        "encoding": "pickle",
        "id": "4a806bb0-be50-4bc5-8481-e8f386e34b39",
        "name": "group_start",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Boolean",
        "usage": "NoPort",
        "value": false
      },
      "dropclass": {
        "defaultValue": "test.graphsRepository",
        "description": "The python class that implements this application",
        "encoding": "pickle",
        "id": "f9a52bcf-2178-40b8-893b-65b5b70099e6",
        "name": "dropclass",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "NoPort",
        "value": "dlg.apps.simple.CopyApp"
      }
    },
    "fields": [
      {
        "defaultValue": "5",
        "description": "Estimate of execution time (in seconds) for this application.",
        "encoding": "pickle",
        "id": "1eea1f1f-674d-4f20-aabc-fb7c09a3c55b",
        "name": "execution_time",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Float",
        "usage": "NoPort",
        "value": 5
      },
      {
        "defaultValue": "1",
        "description": "Number of CPUs used for this application.",
        "encoding": "pickle",
        "id": "4143a443-ae13-4096-a547-278f8a333908",
        "name": "num_cpus",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Integer",
        "usage": "NoPort",
        "value": 1
      },
      {
        "defaultValue": "false",
        "description": "Is this node the start of a group?",
        "encoding": "pickle",
        "id": "4a806bb0-be50-4bc5-8481-e8f386e34b39",
        "name": "group_start",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Boolean",
        "usage": "NoPort",
        "value": false
      },
      {
        "defaultValue": "test.graphsRepository",
        "description": "The python class that implements this application",
        "encoding": "pickle",
        "id": "f9a52bcf-2178-40b8-893b-65b5b70099e6",
        "name": "dropclass",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "NoPort",
        "value": "dlg.apps.simple.CopyApp"
      },
      {
        "defaultValue": "",
        "description": "",
        "encoding": "pickle",
        "id": "2b5dc75a-2588-4ef2-bf5a-b2a22b32ba23",
        "name": "data",
        "options": [],
        "parameterType": "ApplicationArgument",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "InputOutput",
        "value": ""
      }
    ],
    "execution_time": 5,
    "group_start": false,
    "data": "",
    "iid": "0",
    "lg_key": "7e01974d-2611-4358-82e7-c7ef796de0c5",
    "inputs": [
      {
        "test_pg_gen_cd274ac6-7e66-4216-adc2-a13799ea46da_0": "data"
      }
    ],
    "outputs": [
      {
        "test_pg_gen_3779f145-e738-46b2-ac9b-cecee40811a9_0": "data"
      }
    ],
    "node": "10.128.0.12",
    "island": "10.128.0.11",
    "humanReadableKey": "4_0"
  },
  {
    "oid": "test_pg_gen_9aa5cc70-c08b-4c99-9607-64e0436c12ce_0",
    "name": "Python App",
    "categoryType": "Application",
    "category": "PythonApp",
    "dropclass": "dlg.apps.simple.CopyApp",
    "storage": "PythonApp",
    "rank": [
      0
    ],
    "reprodata": {},
    "loop_ctx": null,
    "weight": 5,
    "num_cpus": 1,
    "applicationArgs": {
      "data": {
        "defaultValue": "",
        "description": "",
        "encoding": "pickle",
        "id": "72238898-292f-4a5f-85c0-6474b810caad",
        "name": "data",
        "options": [],
        "parameterType": "ApplicationArgument",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "InputOutput",
        "value": ""
      }
    },
    "constraintParams": {
      "execution_time": {
        "defaultValue": "5",
        "description": "Estimate of execution time (in seconds) for this application.",
        "encoding": "pickle",
        "id": "7edcd9d9-52ed-454c-8be8-931073887518",
        "name": "execution_time",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Float",
        "usage": "NoPort",
        "value": 5
      },
      "num_cpus": {
        "defaultValue": "1",
        "description": "Number of CPUs used for this application.",
        "encoding": "pickle",
        "id": "59fb62ba-6a22-4c17-99eb-957777c0f347",
        "name": "num_cpus",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Integer",
        "usage": "NoPort",
        "value": 1
      }
    },
    "componentParams": {
      "group_start": {
        "defaultValue": "false",
        "description": "Is this node the start of a group?",
        "encoding": "pickle",
        "id": "9eeca514-809f-45ec-b50e-22d3851d4fe5",
        "name": "group_start",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Boolean",
        "usage": "NoPort",
        "value": false
      },
      "dropclass": {
        "defaultValue": "test.graphsRepository",
        "description": "The python class that implements this application",
        "encoding": "pickle",
        "id": "ec146301-22fb-4ac5-af50-2626907c88b9",
        "name": "dropclass",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "NoPort",
        "value": "dlg.apps.simple.CopyApp"
      }
    },
    "fields": [
      {
        "defaultValue": "5",
        "description": "Estimate of execution time (in seconds) for this application.",
        "encoding": "pickle",
        "id": "7edcd9d9-52ed-454c-8be8-931073887518",
        "name": "execution_time",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Float",
        "usage": "NoPort",
        "value": 5
      },
      {
        "defaultValue": "1",
        "description": "Number of CPUs used for this application.",
        "encoding": "pickle",
        "id": "59fb62ba-6a22-4c17-99eb-957777c0f347",
        "name": "num_cpus",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Integer",
        "usage": "NoPort",
        "value": 1
      },
      {
        "defaultValue": "false",
        "description": "Is this node the start of a group?",
        "encoding": "pickle",
        "id": "9eeca514-809f-45ec-b50e-22d3851d4fe5",
        "name": "group_start",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Boolean",
        "usage": "NoPort",
        "value": false
      },
      {
        "defaultValue": "test.graphsRepository",
        "description": "The python class that implements this application",
        "encoding": "pickle",
        "id": "ec146301-22fb-4ac5-af50-2626907c88b9",
        "name": "dropclass",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "NoPort",
        "value": "dlg.apps.simple.CopyApp"
      },
      {
        "defaultValue": "",
        "description": "",
        "encoding": "pickle",
        "id": "72238898-292f-4a5f-85c0-6474b810caad",
        "name": "data",
        "options": [],
        "parameterType": "ApplicationArgument",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "InputOutput",
        "value": ""
      }
    ],
    "execution_time": 5,
    "group_start": false,
    "data": "",
    "iid": "0",
    "lg_key": "9aa5cc70-c08b-4c99-9607-64e0436c12ce",
    "inputs": [
      {
        "test_pg_gen_cd274ac6-7e66-4216-adc2-a13799ea46da_0": "data"
      }
    ],
    "outputs": [
      {
        "test_pg_gen_9f1011e5-6e52-42df-810d-861ea0482747_0": "data"
      }
    ],
    "node": "10.128.0.12",
    "island": "10.128.0.11",
    "humanReadableKey": "5_0"
  },
  {
    "oid": "test_pg_gen_4c44a7b5-02d0-414a-a089-0af4394486f4_0",
    "name": "Shared Memory",
    "categoryType": "Data",
    "category": "SharedMemory",
    "dropclass": "dlg.data.drops.memory.SharedMemoryDROP",
    "storage": "SharedMemory",
    "rank": [
      0
    ],
    "reprodata": {},
    "loop_ctx": null,
    "weight": 5,
    "applicationArgs": {
      "data": {
        "defaultValue": "",
        "description": "",
        "encoding": "pickle",
        "id": "9857a4e2-2f05-4850-bafd-24581f530e32",
        "name": "data",
        "options": [],
        "parameterType": "ApplicationArgument",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "InputPort",
        "value": ""
      }
    },
    "constraintParams": {
      "data_volume": {
        "defaultValue": "5",
        "description": "Estimated size of the data contained in this node",
        "encoding": "pickle",
        "id": "505ecc6f-33be-4ada-a228-3cb8d824906b",
        "name": "data_volume",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Float",
        "usage": "NoPort",
        "value": 5
      }
    },
    "componentParams": {
      "group_end": {
        "defaultValue": "false",
        "description": "Is this node the end of a group?",
        "encoding": "pickle",
        "id": "c9016cc1-838f-45e4-996b-b56b17b4cb38",
        "name": "group_end",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Boolean",
        "usage": "NoPort",
        "value": false
      },
      "dropclass": {
        "defaultValue": "dlg.data.drops.memory.SharedMemoryDROP",
        "description": "",
        "encoding": "pickle",
        "id": "3a4baace-34f1-4b72-932e-582cc4728a89",
        "name": "dropclass",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "NoPort",
        "value": "dlg.data.drops.memory.SharedMemoryDROP"
      }
    },
    "fields": [
      {
        "defaultValue": "5",
        "description": "Estimated size of the data contained in this node",
        "encoding": "pickle",
        "id": "505ecc6f-33be-4ada-a228-3cb8d824906b",
        "name": "data_volume",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Float",
        "usage": "NoPort",
        "value": 5
      },
      {
        "defaultValue": "false",
        "description": "Is this node the end of a group?",
        "encoding": "pickle",
        "id": "c9016cc1-838f-45e4-996b-b56b17b4cb38",
        "name": "group_end",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Boolean",
        "usage": "NoPort",
        "value": false
      },
      {
        "defaultValue": "",
        "description": "",
        "encoding": "pickle",
        "id": "9857a4e2-2f05-4850-bafd-24581f530e32",
        "name": "data",
        "options": [],
        "parameterType": "ApplicationArgument",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "InputPort",
        "value": ""
      },
      {
        "defaultValue": "dlg.data.drops.memory.SharedMemoryDROP",
        "description": "",
        "encoding": "pickle",
        "id": "3a4baace-34f1-4b72-932e-582cc4728a89",
        "name": "dropclass",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "NoPort",
        "value": "dlg.data.drops.memory.SharedMemoryDROP"
      }
    ],
    "data_volume": 5,
    "group_end": false,
    "data": "",
    "iid": "0",
    "lg_key": "4c44a7b5-02d0-414a-a089-0af4394486f4",
    "producers": [
      {
        "test_pg_gen_6c904754-5fd8-4960-aaf6-c1af72dab142_0": "data"
      }
    ],
    "node": "10.128.0.12",
    "island": "10.128.0.11",
    "humanReadableKey": "6_0"
  },
  {
    "oid": "test_pg_gen_9f1011e5-6e52-42df-810d-861ea0482747_0",
    "name": "Shared Memory",
    "categoryType": "Data",
    "category": "SharedMemory",
    "dropclass": "dlg.data.drops.memory.SharedMemoryDROP",
    "storage": "SharedMemory",
    "rank": [
      0
    ],
    "reprodata": {},
    "loop_ctx": null,
    "weight": 5,
    "applicationArgs": {
      "data": {
        "defaultValue": "",
        "description": "",
        "encoding": "pickle",
        "id": "b221cb23-e256-49c5-b3d2-0bc6f2b3c53a",
        "name": "data",
        "options": [],
        "parameterType": "ApplicationArgument",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "InputPort",
        "value": ""
      }
    },
    "constraintParams": {
      "data_volume": {
        "defaultValue": "5",
        "description": "Estimated size of the data contained in this node",
        "encoding": "pickle",
        "id": "b8b0dfb9-ea70-420d-ade1-ee93507c0648",
        "name": "data_volume",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Float",
        "usage": "NoPort",
        "value": 5
      }
    },
    "componentParams": {
      "group_end": {
        "defaultValue": "false",
        "description": "Is this node the end of a group?",
        "encoding": "pickle",
        "id": "13fe9e42-90ec-40df-99f8-d2c60d5f4cf3",
        "name": "group_end",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Boolean",
        "usage": "NoPort",
        "value": false
      },
      "dropclass": {
        "defaultValue": "dlg.data.drops.memory.SharedMemoryDROP",
        "description": "",
        "encoding": "pickle",
        "id": "36031839-e818-4aa9-b2ed-888ae93cd4a1",
        "name": "dropclass",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "NoPort",
        "value": "dlg.data.drops.memory.SharedMemoryDROP"
      }
    },
    "fields": [
      {
        "defaultValue": "5",
        "description": "Estimated size of the data contained in this node",
        "encoding": "pickle",
        "id": "b8b0dfb9-ea70-420d-ade1-ee93507c0648",
        "name": "data_volume",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Float",
        "usage": "NoPort",
        "value": 5
      },
      {
        "defaultValue": "false",
        "description": "Is this node the end of a group?",
        "encoding": "pickle",
        "id": "13fe9e42-90ec-40df-99f8-d2c60d5f4cf3",
        "name": "group_end",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Boolean",
        "usage": "NoPort",
        "value": false
      },
      {
        "defaultValue": "",
        "description": "",
        "encoding": "pickle",
        "id": "b221cb23-e256-49c5-b3d2-0bc6f2b3c53a",
        "name": "data",
        "options": [],
        "parameterType": "ApplicationArgument",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "InputPort",
        "value": ""
      },
      {
        "defaultValue": "dlg.data.drops.memory.SharedMemoryDROP",
        "description": "",
        "encoding": "pickle",
        "id": "36031839-e818-4aa9-b2ed-888ae93cd4a1",
        "name": "dropclass",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "NoPort",
        "value": "dlg.data.drops.memory.SharedMemoryDROP"
      }
    ],
    "data_volume": 5,
    "group_end": false,
    "data": "",
    "iid": "0",
    "lg_key": "9f1011e5-6e52-42df-810d-861ea0482747",
    "producers": [
      {
        "test_pg_gen_9aa5cc70-c08b-4c99-9607-64e0436c12ce_0": "data"
      }
    ],
    "node": "10.128.0.12",
    "island": "10.128.0.11",
    "humanReadableKey": "7_0"
  },
  {
    "oid": "test_pg_gen_3779f145-e738-46b2-ac9b-cecee40811a9_0",
    "name": "Shared Memory",
    "categoryType": "Data",
    "category": "SharedMemory",
    "dropclass": "dlg.data.drops.memory.SharedMemoryDROP",
    "storage": "SharedMemory",
    "rank": [
      0
    ],
    "reprodata": {},
    "loop_ctx": null,
    "weight": 5,
    "applicationArgs": {
      "data": {
        "defaultValue": "",
        "description": "",
        "encoding": "pickle",
        "id": "9b6ec8c5-6cd9-4b0b-a52b-394b018d5bbd",
        "name": "data",
        "options": [],
        "parameterType": "ApplicationArgument",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "InputPort",
        "value": ""
      }
    },
    "constraintParams": {
      "data_volume": {
        "defaultValue": "5",
        "description": "Estimated size of the data contained in this node",
        "encoding": "pickle",
        "id": "16e35c25-8c90-420a-839a-9480230fdfc5",
        "name": "data_volume",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Float",
        "usage": "NoPort",
        "value": 5
      }
    },
    "componentParams": {
      "group_end": {
        "defaultValue": "false",
        "description": "Is this node the end of a group?",
        "encoding": "pickle",
        "id": "9aed6419-e58a-489a-80eb-dd0c5b052591",
        "name": "group_end",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Boolean",
        "usage": "NoPort",
        "value": false
      },
      "dropclass": {
        "defaultValue": "dlg.data.drops.memory.SharedMemoryDROP",
        "description": "",
        "encoding": "pickle",
        "id": "0bcdef8b-6454-4b82-a0ee-7ebddf348164",
        "name": "dropclass",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "NoPort",
        "value": "dlg.data.drops.memory.SharedMemoryDROP"
      }
    },
    "fields": [
      {
        "defaultValue": "5",
        "description": "Estimated size of the data contained in this node",
        "encoding": "pickle",
        "id": "16e35c25-8c90-420a-839a-9480230fdfc5",
        "name": "data_volume",
        "options": [],
        "parameterType": "ConstraintParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Float",
        "usage": "NoPort",
        "value": 5
      },
      {
        "defaultValue": "false",
        "description": "Is this node the end of a group?",
        "encoding": "pickle",
        "id": "9aed6419-e58a-489a-80eb-dd0c5b052591",
        "name": "group_end",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "Boolean",
        "usage": "NoPort",
        "value": false
      },
      {
        "defaultValue": "",
        "description": "",
        "encoding": "pickle",
        "id": "9b6ec8c5-6cd9-4b0b-a52b-394b018d5bbd",
        "name": "data",
        "options": [],
        "parameterType": "ApplicationArgument",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "InputPort",
        "value": ""
      },
      {
        "defaultValue": "dlg.data.drops.memory.SharedMemoryDROP",
        "description": "",
        "encoding": "pickle",
        "id": "0bcdef8b-6454-4b82-a0ee-7ebddf348164",
        "name": "dropclass",
        "options": [],
        "parameterType": "ComponentParameter",
        "positional": false,
        "precious": false,
        "readonly": false,
        "type": "String",
        "usage": "NoPort",
        "value": "dlg.data.drops.memory.SharedMemoryDROP"
      }
    ],
    "data_volume": 5,
    "group_end": false,
    "data": "",
    "iid": "0",
    "lg_key": "3779f145-e738-46b2-ac9b-cecee40811a9",
    "producers": [
      {
        "test_pg_gen_7e01974d-2611-4358-82e7-c7ef796de0c5_0": "data"
      }
    ],
    "node": "10.128.0.12",
    "island": "10.128.0.11",
    "humanReadableKey": "8_0"
  }
]