# Configurations

## ```config_agent.json```

This json file is read by STADLE agents to configure their initial setups.

- ```agent_name```: A unique name of the agent that users can define.
  - e.g. ```default_agent```
- ```model_path```: A path to a local director in the agent machine to save local models and some state info. 
  - e.g. ```"./data/agent"```
- ```local_model_file_name```: A file name to save local models in the agent machine. 
  - e.g. ```lms.binaryfile```
- ```semi_global_model_file_name```: A file name to save the latest semi-global models in the agent machine. 
  - e.g. ```sgms.binaryfile```
- ```state_file_name```: A file name to store the agent state in the agent machine.
  - e.g. ```state```
- ```aggr_ip```: An aggregator IP address for agents to connect.
  - e.g. ```localhost```
- ```reg_port```: A port number used by agents to join an aggregator for the first time.
  - e.g. ```8765```
- ```exh_port```: A port number used to upload local models to an aggregator from an agent. Agents will get to know this port from the communications with an aggregator.
  - e.g. ```0000```
- ```init_weights_flag```: A flag used for initializing weights.
  - e.g. ```1```
- ```simulation```: A flag used to enable a simulation mode.
  - e.g. ```True```
- ```token```: A token that is used for registration process of agents. Agents need to have the same token to be registered in the STADLE system.
  - e.g. ```stadle12345```
