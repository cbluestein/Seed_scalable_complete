Internet Emulator
---

The objective of the SEED-Emulator project is to help create emulators of 
the Internet. These emulators are for educational uses, and they can be
used as the platform for designing hands-on lab exercises for various subjects,
including cybersecurity, networking, etc.

The project provides essential elements of the Internet (as Python classes), including 
Internet exchanges, autonomous systems, BGP routers, DNS infrastructure, 
a variety of services. Users can use these elements as the building blocks
to build their emulation programmatically. The output of the program 
is a set of docker container folders/files. When these containers are built and 
started, they form a small-size Internet. New building blocks are being added,
including Blockchain, Botnet, and many other useful elements of the Internet. 

![The Web UI](docs/assets/web-ui.png)

## Table of Contents

-  [Getting Started](#getting-started)
-  [License](#license)

## Changes to base SEED Simulator

Note this is currently deployed in the base SEED environment only and not converted to the cloudlab deployment yet. You should be able to deploy 60-ish nodes on a laptop that has dedicated 8GB of RAM to the environment. 

1. Added startup scripts to `docker.py` compiler for proxy and ganache (lines `41-71`) and added their startup to the start.sh script (lines `869-877`). 
2. Edited `docker.py` compiler lines `889-909` to add base image configuration to each docker device in the network. This includes all software and packages necessary to run blockchain, smart contract and proxy actions.
3. Added `.env` file of 200 pre-made blockchain accounts representing ASNs 0-199 to https://github.com/KarlOlson/Seed_scalable/bgp_smart_contracts.git in the `/src` directory. This file is used to comply with Greg's account lookup procedures for the smart contracts.
4. Added `accounts.txt` file to `/src` directory to have easily parsable file of accounts. This contains same info as `.env` file, but is space separated.
5. Added `solc_ver_install.py` file to `/src` to pre-install compatability requirements for greg's smart contract. This is installed during docker build now. I did not delete the original from the `compile.py` in order to allow compatability with internet connected systems and completeness of programs. Python will detect installed and skip this in the `compile.py` file.
6. When running `deploy.py` the contract address generated is deterministic and is pre-loaded into the `.env` file. No editing necessary.
7. Added `account_script.py` to `/src`. Running this on `ix100` will deploy the specified ASNs and prefix's to the smart contract. See Account Deployment section for more detail on operation.
8. Added `proxy.py` to `/src`. This is slightly different from the EVE environment in that it works by listening on all local interfaces rather than via a pass-through proxy. 

## Getting Started

To get started with the emulator:
1. Clone this repository into your environment (Windows or Linux or a VM).
2. Install docker, docker-compose, and python3 in your environment. 
3. If you require more than the 200 pre-defined blockchain accounts you should pre-establish them now and update the `bgp_smart_contracts/src/.env` file and the `accounts.txt` file with the additional accounts. You can create accounts by running `ganache -a <# of accounts> --deterministic` from any device with ganache installed. The deterministic flag will result in the same account info regardless of system. In the seed emulator, this can be run on the `ix100` system. Just copy and paste the generated data into the `.env` and `.txt` files following the same formatting (different for each file).

## Running a BGP and blockchain Scenario in SEED
1. Add `seedemu` to `PYTHONPATH`. This can be done by running `source development.env` under the project root directory or running `export PYTHONPATH="`pwd`:$PYTHONPATH" from the root seed directory.
1. Pre-built scenarios are located in the `/examples` folder. 
2. Pick an example, say `A00-simple-peering`. 
3. Build the emulation. For this example, cd to `examples/A00-simple-peering/`, and run `python3 ./simple-peering.py`. The container files will be created inside the newly generated `output/` folder in the same directory. For some examples, such as `B02-mini-internet-with-dns`, they depend on other examples, so you need to run those examples first. This is part of our component design.
4. Build and run the containers. First `cd output/`, then do `docker-compose build && docker-compose up`. The emulator will start running. Give it a minute or two (or longer if your emulator is large) to let the routers do their jobs. If this is a first build it can take about 40 minutes to build the containers.
5. Optionally, start the seedemu web client. Open a new terminal window, navigate to the project root directory, cd to `client/`, and run `docker-compose build && docker-compose up`. Then point your browser to `http://127.0.0.1:8080/map.html`, and you will see the entire emulator. Use the filter box if you want to see the packet flow.
6. It doesn't quite appear that ganache is fully automated to start yet and seems like I have to manually enable it one the environment launches. Go into the seed web client, click on the `ix100` device and then click `connect`. This will bring up the command prompt for that device. Deploy ganache by entering `$ ganache -a 200 -p 8545 -h 10.100.0.100 --deterministic`. Optionally, you can add `--database.dbPath /ganache` if you want to store and maintain the updates on the chain. I typically dont. 
7. Establish the contract and the initial conditions by running `$python3 compile.py` followed by `python3 deploy.py ACCOUNT0`. This can be done from any device as they are all pre-loaded with these scripts. Once this is setup, you can run `account_script.py` to bulk deploy ASNs and Prefix's to the contract. Within here you can specify the ASNs you want authorized for the chain by defining line 16 values. So if you pick `asn_number=[151,152]` as the values, this will load the blockchain by assigning those ASNs to Account 151 and Account 152 along with their prefixes: 10.151.0.0/24 and 10.152.0.0/24. Those routers will then have to validate their actions on the chain when advertising.
8. Validate and view proxy implementation on routing devices. Proxy should be running on each routing device. If not, you can manually deploy by running: `/bgp_smart_contracts/src/proxy.py` code to launch the proxy to begin intercepting packets and validating BGP packets with blockchain. 

## Known issues/To be worked.

1. Looks like when deploying larger ASN counts that everything begins at 150 and counts upward. So the first 150 ganache accounts don't really provide any value at the moment. Not an issue, but something to be aware of. 
2. I made new repositories on my account and set to public for easy update/changes. I can switch back, but one of Greg's was private and required entering my gpd key and programming that in to the compiler in order to pull. I am sure there is a way to automate without hard coding a password token in...but haven't got there. This was a quick test/fix.
3. The proxy stops/locks when using the graphical `disconnect` is used to stop/re-enable the bgp routing in seed.
4. Not an issue, but something to be aware of: The proxies are configured to only act on their own or neighbor updates. So changes occuring 2+ routers away do not trigger chain lookups.

## Key Files:
1. `/bgp_smart_contracts/src/.env` contains all the account info and location of system running the ganache chain. Used by all the blockchain setup scripts.
2. `/bgp_smart_contracts/src/solc_ver_install.py` script run by docker to pre-load solc version used by smart contracts. Currently set to 0.8.0 to support Greg's scripts.
3. `/bgp_smart_contracts/src/accounts.txt` contains same account info as .env but in a more python friendly parsable format.
4. `/bgp_smart_contracts/src/proxy.py` code to launch blockchain-integrated proxy for capturing and assessing BGP advertisements.
5. `/bgp_smart_contracts/src/compile.py` compiles smart contract
6. `/bgp_smart_contracts/src/deploy.py` deploys smart contract on ganache blockchain
7. `/bgp_smart_contracts/src/add_asn.py` establishes new ASNs within the smart contract
8. `/bgp_smart_contracts/src/add_prefix.py` assigns prefixes to ASNs within the smart contract
9. `Seed_scalable/seedemu/compiler/docker.py` compiler script used to build containers for both local and distrubuted environments (the distributed_docker.py calls on this to build the containers first). Edit this file if you need to change any containers with pre-loaded requirements.

## Terraform and Google Cloud Deployment
You can use SEED to build a terraform project and then deploy that to google cloud programmatically. This will walk you thorugh steps necessary to deploy in GCP.

### Google Cloud Setup
1. Go to https://cloud.google.com/ and establish an account. You will get $300 in compute time credit (you will need a credit card to verify yourself, but it is never charged, even after use of credits). 
2. Once you have an account, the first thing you will need to define is a new project. If first time, this should be your landing page. If not, in top left of screen is a drop down (next to the three line menu), select that and do `New Project`. 
3. Now you need to creat a service account that will be used by the Terraform environment to deploy everything to the cloud. A service account is just like any other account, but you can control permissions and such separately to control settings as you see fit. To create a service account that will be used by Terraform, click the 3 line menu in the top left of the screen, select `IAM & Admin ->Service Accounts`. Then select `Create new account`. Give it a name like `terraform` and then click next. On role, assign it `compute admin` and then click `continue`. Click done. Update: for later/larger configurations with firewalls, etc. you will need additional permissions: Compute Instance Admin v1, Compute network admin, Compute security admin, compute.firewalls.create (create a new role and assign this separately).
4. Add keys to your service account. You should see your account created, but no keys assigned. On the far right, click the three dots to bring up a menu. Then click `manage keys`. Select `add key->create new key` and then select .json as your output. A new public key will be added to your account. The private key is automatically downloaded so check your downloads. You will need to move this key to the directory that contains your terraform files. 

### SEED VM Setup
1. For the most part everything should be set up with seed. There are two changes that you need to make in order to compile to a terraform output and then deploy the terraform environment. 
2. The first thing you need to change is compilation script to select your chosen output method. In this script change your compiler to GcpDistributedDocker() prior to compilation. 
3. Run the compilation script for your project to generate the output files and directory which should include all the terraform scripts.
4. Prior to deploying in terraform, you will likely need to install `jq` on your host. This is used for key generation for terraform containers. The errors don't really clue you in to the fact that this package is likely missing, so if you get a warning that 'ssh-keygen' failed, this is likely the issue. Just run a `sudo apt-get install -y jq` and you should have everything needed to run terraform.

### Terraform Deployment
1. To run execute `terraform init` from your root project directory (the one with main.tf file). Make sure you have your Google cloud .json key in this directory form the earlier steps. Running init will ask a few questions about your targeted google cloud environment. For `Path to credential JSON file` enter the path to where you placed your private key (should be the same location as the main.tf file). For `Project ID`, this can be found under `IAM & Admin - > Settings` and then grab the number under `Project Number`. For `Region` and `Zone` you can pick any of the options from google. If no idea, pick `us-west4` for Region and `us-west4-b` for zone. 
2. Everything should now deploy. Give it about 5 minutes and you should see everything deployed in your Google cloud project under the `compute` resource (under the menu). Each IX will deploy on a docker swarm `master` node and each AS will deploy on its own `worker` node. All items associated with an AS will deploy on the same worker node. 


## License

The software is licensed under the GNU General Public License v3.0 license, with copyright by The SEED-Emulator Developers (see [LICENSE](./LICENSE.txt)).
