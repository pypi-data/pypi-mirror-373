from __future__ import annotations
import tempfile
import tarfile
from bs4 import BeautifulSoup
import json
import os
import requests
from pathlib import Path
import shutil
import git

################### Download tarballs from git ###############################
public_repo =  "AIAmplitudes/Phase1_data"
private_repo =  "AIAmplitudes/data_public"

def _cache_path(cache_dir: str | None = None, make_tarfdir = True) -> Path:
    if cache_dir is None:
        ampdir = Path.home() / ".local" / "AIAmplitudesData"
        try:
            ampdir.mkdir(exist_ok=True, parents=True)
        except:
            print('Could not make dir. Defaulting to local cache')
            os.mkdir('./cache')
            ampdir='./cache'
        return Path(ampdir)

    if make_tarfdir:
        tarfdir = ampdir / "tarfiles"
        tarfdir.mkdir(exist_ok=True, parents=True)

    return Path(cache_dir)

relpath = _cache_path(None)

def clear_cache():
    os.system(f'rm -rf {relpath}')

def get_gitfilenames(the_zipurl):
    soup = BeautifulSoup(requests.get(the_zipurl).text)
    files=[]
    for elem in soup.find_all('script', type='application/json'):
        if ".tar" in elem.text:
            files += [i["name"] for i in json.loads(elem.contents[0])["props"]["initialPayload"]["tree"]["items"]]
    return files

def download_unpack(myfile: str, local_dir: Path, tarfdir = None):
    with tempfile.TemporaryFile() as f:
        with requests.get(myfile, stream=True) as r:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        f.seek(0)
        with tarfile.open(fileobj=f) as tarf:
            for n in tarf.getnames():
                assert os.path.abspath(os.path.join(local_dir, n)).startswith(str(local_dir))
            tarf.extractall(path=local_dir)
        if tarfdir: shutil.move(f"{str(local_dir)}/{myfile}",
                                f"{str(tarfdir)}/{f}")
    return

def download_all_public(repo: str = public_repo, cache_dir: str | None = None) -> None:
    #use BS4 to get all the datasets in the public repo
    local_dir = _cache_path(cache_dir)
    if not len(os.listdir(local_dir))==0:
        print("Local cache not empty! Terminating")
        return
    print(f"downloading files from {repo}, unpacking in {local_dir}")
    url=f"https://github.com/{repo}"
    for file in get_gitfilenames(url):
        if not ".tar" in file: continue
        myfile = f"https://raw.githubusercontent.com/{repo}/main/{file}"
        print(f"extracting {myfile}")
        download_unpack(myfile,local_dir)

    #dump all files into the root directory
    for subdir, dirs, files in os.walk(local_dir):
        if "tarfiles" in subdir: continue
        if ".git" in subdir: continue
        for file in files:
            os.rename(str(os.path.join(subdir, file)),str(os.path.join(local_dir, file)))

    #delete all subdirs that do not have a file in them
    deleted=set()
    for thisdir, subdirs, files in os.walk(local_dir, topdown=False):
        still_has_subdirs = False
        for subdir in subdirs:
            if os.path.join(thisdir, subdir) not in deleted:
                still_has_subdirs = True
                break
        if not any(files) and not still_has_subdirs:
            os.rmdir(thisdir)
            deleted.add(thisdir)
    return

def download_all_private(username,mytoken, repo: str = public_repo, cache_dir: str | None = None) -> None:
    #use the github CLI and token access to get datasets in the private repo
    local_dir = _cache_path(cache_dir)
    git_url = f"https://{username}:{mytoken}@github.com/AIAmplitudes/data_public.git"
    git.Repo.clone_from(git_url, local_dir)
    tarfdir = local_dir / "tarfiles"
    tarfdir.mkdir(exist_ok=True, parents=True)
    for f in os.listdir(local_dir):
        if ".tar" in f:
            mytar = f"{local_dir}/{f}"
            with tarfile.open(mytar) as tarf:
                for n in tarf.getnames():
                    assert os.path.abspath(os.path.join(local_dir, n)).startswith(str(local_dir))
                tarf.extractall(path=local_dir)
            shutil.move(mytar, f"{str(tarfdir)}/{f}")

    #dump all files into the root directory
    for subdir, dirs, files in os.walk(local_dir):
        if ".git" in subdir: continue
        if "tarfiles" in subdir: continue
        for file in files:
            os.rename(str(os.path.join(subdir, file)),str(os.path.join(local_dir, file)))

    #delete all subdirs that do not have a file in them
    deleted=set()

    for thisdir, subdirs, files in os.walk(local_dir, topdown=False):
        if "tarfiles" in str(thisdir): continue
        if ".git" in str(thisdir): continue
        still_has_subdirs = False
        for subdir in subdirs:
            if os.path.join(thisdir, subdir) not in deleted:
                still_has_subdirs = True
                break
        if not any(files) and not still_has_subdirs:
            os.rmdir(thisdir)
            deleted.add(thisdir)
    return

def download_all(username= None, mytoken = None):
    if len(os.listdir(relpath)) != 0:
        clear_cache()
    if not username or not mytoken:
        username = input("Github user:")
        mytoken = input("Github access token:")
    try:
        download_all_private(username, mytoken)
    except git.exc.GitCommandError:
        print("github access error- defaulting to phase 1 data download only")
        download_all_public()
    return



#######################################################################################

if __name__ == "__main__":
    download_all()