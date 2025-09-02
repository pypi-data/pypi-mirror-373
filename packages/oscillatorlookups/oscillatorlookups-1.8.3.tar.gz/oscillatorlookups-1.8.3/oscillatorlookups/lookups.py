import asyncio
import itertools
import os.path
import time

from aiofiles import open as aio_open
import aiohttp
import requests
import msgspec


class Model(msgspec.Struct):
    """A new type describing a Tellurium Model"""
    modelType: str
    path: str
    numSpecies: int
    numReactions: int


def request_metadata(checksum, url):
    """
    makes a web request for the metadata file. Writes the data to file and returns it
    :param url: the url from which the metadata file is requested
    :param checksum: the checksum for the metadata, used to verify that it's up-to-date
    :return: the metadata that has been requested
    """
    data = requests.get(url
                        ).text
    with open("../../metadata.json", "w") as f:
        f.write(data)
    with open("../../checksum", "w") as f:
        f.write(checksum)
    return msgspec.json.decode(data, type=list[Model])


def get_metadata(repoURL: str):
    """
    gets metadata, either from github or from the filesystem, depending on the checksum state
    :param repoURL: the url of the github repo where the metadata is stored
    :return: the metadata
    """
    rawUrl = "https://raw.githubusercontent.com/" + repoURL.split("/")[3] + "/" + repoURL.split("/")[4] + "/refs/heads/master/"
    checksum = requests.get(
        rawUrl + "checksum").text
    if not os.path.isfile("../../checksum") or not os.path.isfile("../../metadata.json"):
        return request_metadata(checksum, rawUrl + "metadata.json")
    with open("../../checksum", "r") as f:
        loadck = f.read()
    if checksum != loadck:
        return request_metadata(checksum, rawUrl + "metadata.json")
    with open("../../metadata.json", "r") as f:
        return msgspec.json.decode(f.read(), type=list[Model])


async def downloadAntString(url, session, resultant_dir):
    """
    downloads an antimony string and stores it in a given directory
    :param url: the url from which to download
    :param session: async session used to make the web request
    :param resultant_dir:
    :return:
    """
    try:
        async with session.get(url=url) as response:
            resp = await response.text()
            async with aio_open(os.path.join(resultant_dir, url.split("/")[-1]), 'w') as f:
                await f.write(resp)
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))


async def lookup(data: list[Model], repoURL:str, resultant_dir: str, num_species: int = None, num_reactions: int = None,
                 model_type=None, ):
    """
    lookup and download tellurium models to the filesystem based on provided criteria
    :param data: list of metadata for models
    :param resultant_dir: directory to which the files should be downloaded
    :param num_species: number of species
    :param num_reactions: number of reactions
    :param model_type: type of model
    """
    rawUrl = "https://raw.githubusercontent.com/" + repoURL.split("/")[3] + "/" + repoURL.split("/")[4] + "/refs/heads/master/"
    paths = []
    for item in data:
        if (num_species is None or item.numSpecies == num_species) and \
                (num_reactions is None or item.numReactions == num_reactions) and \
                (model_type is None or item.modelType == model_type):
            paths.append(
                rawUrl + item.path)
    if not os.path.isdir(resultant_dir):
        os.mkdir(resultant_dir)
    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*(
            downloadAntString(url, session,
                              resultant_dir) for url in paths))

async def lookup_range(data: list[Model], repoURL:str, resultant_dir: str, num_species: range = None, num_reactions: range = None,
                 model_type=None, ):
    """
    lookup and download tellurium models to the filesystem based on provided criteria
    :param data: list of metadata for models
    :param resultant_dir: directory to which the files should be downloaded
    :param num_species: number of species as a range
    :param num_reactions: number of reactions as range
    :param model_type: type of model
    """
    rawUrl = "https://raw.githubusercontent.com/" + repoURL.split("/")[3] + "/" + repoURL.split("/")[4] + "/refs/heads/master/"
    paths = []
    for item in data:
        if (num_species is None or item.numSpecies in num_species) and \
                (num_reactions is None or item.numReactions in num_reactions) and \
                (model_type is None or item.modelType in model_type):
            paths.append(
                rawUrl + item.path)
    if not os.path.isdir(resultant_dir):
        os.mkdir(resultant_dir)
    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*(
            downloadAntString(url, session,
                              resultant_dir) for url in paths))


def get_summary(data: list[Model], asString: bool = False):
    """
    get a summary of the models currently in the database
    :param data: list of metadata for models
    :param asString: whether the summary should be returned as a string, or as a dictionary
    :return: the summary of the database, including the total amount of models and the number of models for each combination of reactions, species, and model type
    """
    if (asString):
        summary = "Total amount of models: " + len(data).__str__()
    else:
        summary = {
            "total amount of models": len(data),
        }
    reaction_nums = {item.numReactions for item in data}
    species_nums = {item.numSpecies for item in data}
    model_types = {item.modelType for item in data}

    combinations = itertools.product(
        reaction_nums,
        species_nums,
        model_types
    )
    for nr, ns, mt in combinations:
        amnt = len([item.path for item in data if
                    item.numSpecies == ns and item.numReactions == nr and item.modelType == mt])
        if (amnt != 0):
            if (asString):
                summary += f"\nAmount of {mt} models with {nr} reactions and {ns} species: " + amnt.__str__()
            else:
                summary[f"Amount of {mt} models with {nr} reactions and {ns} species"] = amnt
    return summary


def get_model_type_info(data: list[Model]):
    """
    Get the amount of model types, as well as a list thereof
    :param data: list of metadata for models
    :return: a dictionary containing the amount of model types (typesAmount), and a list thereof (types)
    """
    typesSet = {item.modelType for item in data}
    return {"typesAmount": len(typesSet), "types": typesSet}


def get_accepted_ranges(data: list[Model], reactions: bool = True, species: bool = True):
    """
    gets the range of reactions and/or species that are represented in the database
    :param data: list of metadata for models
    :param reactions: whether to get the range of reactions
    :param species: whether to get the range of species
    :return: a dictionary containing the range of reactions (reactionsRange) and/or species (speciesRange) represented in the database, depending on params.
    """
    dicts = {}
    if reactions:
        dicts["reactionsRange"] = ({item.numReactions for item in data})
    if species:
        dicts["speciesRange"] = ({item.numSpecies for item in data})
    for key in dicts.keys():
        dicts[key] = (min(dicts[key]), max(dicts[key]))
    return dicts


def get_number_of_models_with_attrib(data: list[Model], num_species:int=None, num_reactions:int=None, model_type=None):
    """
    counts the amount of models with certain attributes that exist in the database
    :param data: list of metadata for models
    :param num_species: number of species
    :param num_reactions: number of reactions
    :param model_type: type of model
    :return: the amount of models with the given attributes that exist in the database
    """
    count = 0
    for item in data:
        if (num_species is None or item.numSpecies == num_species) and \
                (num_reactions is None or item.numReactions == num_reactions) and \
                (model_type is None or item.modelType == model_type):
            count += 1
    return count


'''
start = time.time()
metadata = get_metadata("https://github.com/epshteinmatthew/OscillatorDatabase")
print(time.time() - start)

#example: print a summary of the dataset
e = get_summary(metadata, asString=False)
for line in e:
    print(line + ":" + e[line].__str__())

#example: print the amount of models with 3 species and of type oscillator
print(get_number_of_models_with_attrib(metadata, num_species=3, model_type="oscillator"))

#example: lookup models with 3 species and 3 reactions, and put them into the "osc123" directory
asyncio.run(lookup(metadata, "https://github.com/epshteinmatthew/OscillatorDatabase","osc123/" ,3, 4, "oscillator"))
end = time.time()
print(end - start)
'''
