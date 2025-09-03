import fsspec
import json 
import os 
from tqdm.notebook import tqdm 
import shutil
import pandas as pd 


def rm(path, bucket='dmitrij',
       endpoint="https://8a6ab2cee54f34a71f5a8d99e92da2d2.r2.cloudflarestorage.com",
       verbose=True):

    fs = fsspec.filesystem(
        "s3",
        profile="r2",
        client_kwargs={"endpoint_url": endpoint, "use_ssl": True},
        config_kwargs={"s3": {"addressing_style": "path"}}
    )
    target = f"s3://{bucket}/{path}"
    if verbose:
        print(f"Deleting {target}...")
    fs.rm(target)


def done(fasta_folder='000',
         structure_folder='',
         bucket='dmitrij',
         endpoint="https://8a6ab2cee54f34a71f5a8d99e92da2d2.r2.cloudflarestorage.com",
         load_local_cache=True,
         load_s3_cache=True,
         verbose=True,
         pbar=True,
        ):

    fs = fsspec.filesystem(
            "s3",
            profile="r2",
            client_kwargs={
                "endpoint_url": endpoint,
                "use_ssl": True,
            },
            config_kwargs={
                "s3": {"addressing_style": "path"}
            }
    )
    structure_folder = 'foldify_' + fasta_folder if structure_folder == '' else structure_folder
    remote_fastas = fs.ls(f"s3://{bucket}/{fasta_folder}", detail=True)
    remote_zips = fs.ls(f"s3://{bucket}/{structure_folder}", detail=True) # this is 10it/s; parallelize somehow?
    return remote_zips, remote_fastas


def ls(
    bucket = 'dmitrij',
    endpoint="https://8a6ab2cee54f34a71f5a8d99e92da2d2.r2.cloudflarestorage.com"
    ):
  fs = fsspec.filesystem(
            "s3",
            profile="r2",
            client_kwargs={
                "endpoint_url": endpoint,
                "use_ssl": True,
            },
            config_kwargs={
                "s3": {"addressing_style": "path"}
            }
  
    )
  remote = fs.ls(f"s3://{bucket}", detail=True)
  return ['/'.join(a['Key'].split('/')[1:]) for a in remote]


# make simple ls/rm command? 
# i.e., if logged in, we can just ls/rm as normal
# 

def ls(
  bucket = 'dmitrij',
  endpoint="https://8a6ab2cee54f34a71f5a8d99e92da2d2.r2.cloudflarestorage.com"
):
  fs = fsspec.filesystem(
            "s3",
            profile="r2",
            client_kwargs={
                "endpoint_url": endpoint,
                "use_ssl": True,
            },
            config_kwargs={
                "s3": {"addressing_style": "path"}
            }
  
    )
  remote = fs.ls(f"s3://{bucket}", detail=True)
  return ['/'.join(a['Key'].split('/')[1:]) for a in remote]

  


def ls_folder(  bucket = 'dmitrij',
    endpoint="https://8a6ab2cee54f34a71f5a8d99e92da2d2.r2.cloudflarestorage.com"):
    from natsort import natsorted
  

    folders = [folder for folder in ls(bucket=bucket, endpoint=endpoint) if '.' not in folder 
               ]
    return natsorted(folders )


# merge two versions -- then rebuild foldifyai and redo plot in colab! 

def load(fasta_folder='000',
         structure_folder='',
         bucket='dmitrij',
         endpoint="https://8a6ab2cee54f34a71f5a8d99e92da2d2.r2.cloudflarestorage.com",
         use_local_cache=True,
         use_s3_cache=True,
         verbose=True,
         pbar=True,
         wipe_cache=False
        ):

    if structure_folder == '': structure_folder = 'foldify_' + fasta_folder
    if os.path.exists(f"{structure_folder}.csv") and use_local_cache:
        if verbose: print(f"[foldify] Found `{structure_folder}.csv` locally.")
        return pd.read_csv(f"{structure_folder}.csv")

    fs = fsspec.filesystem(
            "s3",
            profile="r2",
            client_kwargs={
                "endpoint_url": endpoint,
                "use_ssl": True,
            },
            config_kwargs={
                "s3": {"addressing_style": "path"}
            }

    )


 

    if fs.exists( f"s3://{bucket}/{structure_folder}.csv") and use_s3_cache:
        if verbose: print(f"[foldify] Found `{structure_folder}.csv` on s3.")
        fo = fsspec.open(
            f"{'' if wipe_cache else 'simplecache::'}s3://{bucket}/{structure_folder}.csv",
            mode="r",
            s3={"profile": "r2",
                "client_kwargs": {"endpoint_url": endpoint, "use_ssl": True},
                "config_kwargs": {"s3": {"addressing_style": "path"}},
                
                },
              skip_instance_cache=True
        )
        df = pd.read_csv(fo.open())
        os.makedirs(os.path.dirname(structure_folder), exist_ok=True)
        df.to_csv(f"{structure_folder}.csv")
        return df

    # --- sync 000 (fasta files) ---
    p = f"s3://{bucket}/{fasta_folder}"
    remote = fs.ls(p, detail=True)
    os.makedirs(f"{fasta_folder}", exist_ok=True)
    for f in tqdm(remote, desc=f"s3 -> {fasta_folder}") if pbar else remote:
        local = f['Key'].replace(f'{bucket}/','')
        if not os.path.exists(local) or os.stat(local).st_size != f["Size"]:
            fs.get(f["Key"], str(local))

    # --- sync foldify_000 (zip files, then unzip) ---
    p = f"s3://{bucket}/{structure_folder}"
    remote = fs.ls(p, detail=True) # this is 10it/s; parallelize somehow?
    os.makedirs(f"{structure_folder}", exist_ok=True)
    for f in tqdm(remote, desc=f"s3 -> {structure_folder}") if pbar else remote:
        local = f['Key'].replace(f'{bucket}/', '')
        if not os.path.exists(local) or os.stat(local).st_size != f["Size"]:
            fs.get(f["Key"], str(local))

    # unzip local files
    files = [a for a in os.listdir(f"{structure_folder}") if a[-4:] == ".zip"]
    for local in tqdm(files, desc=f"{structure_folder} -> unzip") if pbar else files:
        if local.endswith(".zip") and not os.path.exists(f"{structure_folder}/{local[:-4]}"):
            shutil.unpack_archive(f"{structure_folder}/{local}", f"{structure_folder}/{local[:-4]}")

    fastas = os.listdir(f"{fasta_folder}")
    df = []
    for fasta in fastas:
        path1, path2 = f'{fasta_folder}/{fasta}', f'{structure_folder}/{fasta[:-6]}/boltz2_input.fasta'
        if not os.path.exists(path1): continue  # deal with this not existing when adding to dataframe
        if not os.path.exists(path2): continue
        lines1 = open(path1, 'r').read().split('\n')
        lines2 = open(path2, 'r').read().split('\n')
        seqs1, seqs2 = lines1[1::2], lines2[1::2]
        if not all([s1 == s2 for s1, s2 in zip(seqs1, seqs2)]):
            print( f"Sequences in {fasta} do not match boltz2_input.fasta\n" + str(seqs1) + "\n"+str(seqs2) + "\n" +\
                path1 + "\n" + path2)

        a3ms = [a for a in lines1 if ".a3m" in a]
        # todo check a3ms

        folder = fasta.replace('.fasta', '')
        path = f"{structure_folder}/{folder}/boltz2_confidence_0.json"
        if os.path.exists(path):
          dct = json.load(open(path, "r"))
          dct['filename']=fasta
          df.append(dct)
        else:
            pass # didn't finish this particular entry for some reason -- add to df somehow.


    df = pd.DataFrame(df)
    df.to_csv(f"{structure_folder}.csv")

    with fs.open(f"s3://{bucket}/{structure_folder}.csv", "w") as f:
        df.to_csv(f, index=False)

    return df
def upload_folder(
    folder,
    bucket="dmitrij",
    prefix="decile2",
    endpoint="https://8a6ab2cee54f34a71f5a8d99e92da2d2.r2.cloudflarestorage.com",
    verbose=True,
):
    fs = fsspec.filesystem(
        "s3",
        profile="r2",
        client_kwargs={"endpoint_url": endpoint, "use_ssl": True},
        config_kwargs={"s3": {"addressing_style": "path"}},
    )

    target_prefix = f"{bucket}/{prefix}/{os.path.basename(folder)}"

    for root, _, files in os.walk(folder):
        for file in tqdm(files):
            local_path = os.path.join(root, file)
            rel_path = os.path.relpath(local_path, folder)
            rel_path = '/'.join(folder.split('/')[-2:]) + local_path.split('/')[-1]
            remote_path = f"{target_prefix}{rel_path}"
            if verbose:
                print(f"Uploading {local_path} -> {remote_path}")
            
            fs.put_file(local_path, remote_path, asynchronous=True)

