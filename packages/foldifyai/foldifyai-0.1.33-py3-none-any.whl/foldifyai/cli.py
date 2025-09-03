"""Command-line interface entrypoint for the `foldifyai` package."""
from __future__ import annotations
import time 
from colorama import Fore, Style
import hashlib 
import fsspec
import numpy as np 

logo = f"{Fore.BLUE}{Style.BRIGHT}[Foldify]{Style.RESET_ALL}"

import base64
import zipfile
import io
import pathlib
import sys
from pathlib import Path
from tqdm import tqdm
import os 
import time 
import json 
from rdkit import Chem
from rdkit.Chem import AllChem
import urllib
from foldifyai.utils import get_type, file_exists
import requests
import fsspec

try: 
    from logmd import LogMD
except:
    pass 


def _usage() -> None:
    """Print a short help message using the actual executable name."""
    prog = pathlib.Path(sys.argv[0]).name or "foldify"
    print(f"Usage: {prog} <path_to_file.fasta>", file=sys.stderr)


def compute_3d_conformer(mol, version: str = "v3") -> bool:
    if version == "v3":
        options = AllChem.ETKDGv3()
    elif version == "v2":
        options = AllChem.ETKDGv2()
    else:
        options = AllChem.ETKDGv2()

    options.clearConfs = False
    conf_id = -1

    options.timeout = 3 # don't spend more than three seconds on AllChem.EmbedMolecule
    #options.maxIterations = 10 # don't spend more than 10 attempts (default is 100?)

    try:
        conf_id = AllChem.EmbedMolecule(mol, options)#, maxAttempts=0)

        if conf_id == -1:
            print(
                f"WARNING: RDKit ETKDGv3 failed to generate a conformer for molecule "
                f"{Chem.MolToSmiles(AllChem.RemoveHs(mol))}, so the program will start with random coordinates. "
                f"Note that the performance of the model under this behaviour was not tested."
            )
            options.useRandomCoords = True
            return False # conf_id = AllChem.EmbedMolecule(mol, options)

        #AllChem.UFFOptimizeMolecule(mol, confId=conf_id, maxIters=1000)
        # i set the maxIters=33 to skip more aggressively.
        AllChem.UFFOptimizeMolecule(mol, confId=conf_id, maxIters=33)

    except RuntimeError:
        return False 
        pass  # Force field issue here
    except ValueError:
        return False 
        pass  # sanitization issue here

    if conf_id != -1:
        conformer = mol.GetConformer(conf_id)
        conformer.SetProp("name", "Computed")
        conformer.SetProp("coord_generation", f"ETKDG{version}")
        return True

    return False

def test(seq, affinity=False):
    from pathlib import Path
    import hashlib

    cache_dir = Path.home() / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256(seq.encode()).hexdigest()
    f = cache_dir / h
    if f.exists(): 
        #print(f'hit ligand test cache {seq}')
        s = f.read_text()
        return "ok" in s, s  # cache mechanism 
    else: 
        #print(f"didn't find ligand test cache {seq}, testing...")
        pass

    try:
        mol = AllChem.MolFromSmiles(seq)
        mol = AllChem.AddHs(mol)

        # Set atom names
        canonical_order = AllChem.CanonicalRankAtoms(mol)
        for atom, can_idx in zip(mol.GetAtoms(), canonical_order):
            atom_name = atom.GetSymbol().upper() + str(can_idx + 1)
            if len(atom_name) > 4:
                msg = (
                    f"{seq} has an atom with a name longer than "
                    f"4 characters: {atom_name}."
                )
                (cache_dir / h).write_text("fail\n" + msg)
                #raise ValueError(msg)
                return False, msg
            atom.SetProp("name", atom_name)

        success = compute_3d_conformer(mol)
        if not success:
            msg = f"Failed to compute 3D conformer for {seq}"
            (cache_dir / h).write_text("fail\n" + msg)
            return False, msg

        mol_no_h = AllChem.RemoveHs(mol, sanitize=False)
        affinity_mw = AllChem.Descriptors.MolWt(mol_no_h) if affinity else None
        (cache_dir / h).write_text("ok")
        return True, ""
    except Exception as e:
        print(e, seq)
        (cache_dir / h).write_text("fail\n" + str(e))
        return False, str(e)

def wait_on_server(host):
    d = {0: '-', 1: '/', 2: '\\', 3: '|', 4: '.'}
    i = 0 
    t0 = time.time()
    while True:
        url = f"{host}/ping"
        try:
            text = urllib.request.urlopen(url).read().decode()
            j = json.loads(text)
            if j['alive']: return
        except:
            t = time.time()-t0
            print(f'\rWaiting on server: {t:.2f}s {d[i%len(d)]}', end='')
            i+=1
            time.sleep(0.2)

LOCAL = 0
S3 = 1

def fold(args):
    folder = args.input
    log = args.logmd 

    mode = None 
    if args.s3 != '':
        fs = fsspec.filesystem(
            "s3",
            profile="r2",
            client_kwargs={
                "endpoint_url": args.s3,
                "use_ssl": True,
            },
            config_kwargs={
                "s3": {"addressing_style": "path"} 
            }
        )
        print(f"{logo} Using s3 filesystem (not local). ")
        mode = S3
        path = args.input[5:]
    else: 
        print(f"{logo} Using local filesystem (not s3). ")
        fs = fsspec.filesystem("file")
        path = args.input
        mode = LOCAL


    # single file 
    if args.input.endswith('.fasta'):
        files = [args.input]
        folder = folder.replace('.fasta', '')
    # directory 
    else:
        #files = fs.glob(f"{path}*.fasta")
        #files = fs.glob(f"{path}*.fasta", recursive=True)
        print(path)
        #lst_path = f"{path}/**/*.fasta"
        #fs.invalidate_cache(lst_path)
        #files = fs.glob(lst_path)
        all_files = fs.find(path)  
        files = [f for f in all_files if f.endswith(".fasta")]  

        print(files)
        if args.msa_s3_precompute:
            print(f'num total files {len(files)}')
            files = np.unique(files).tolist()
            print(f'num unique files {len(files)}')
        files = sorted(files, key=lambda p: int(fs.size(p)))
        path = path.split('/')
        path = path[:1] + ['foldify_' + path[1]] + path[2:]
        path = "/".join(path)
        done = fs.glob(f"{path}*.zip")
        zip_ids = {x.split('/')[-1].rsplit('.', 1)[0] for x in done}

        if mode == S3:      left = [f"s3://{f}" for f in files if f.split('/')[-1].rsplit('.', 1)[0] not in zip_ids]
        elif mode == LOCAL: left = [f for f in files if f.split('/')[-1].rsplit('.', 1)[0] not in zip_ids]

        print(f"{logo} Total: \t", len(files))
        print(f"{logo} Done: \t", len(done))
        print(f"{logo} Left: \t", len(left))
        files = left


    if log: l = LogMD()

    wait_on_server(args.host)

    cache_folder = f"{args.chunks}_{args.msas_num}_{args.msas_top_fft}_{args.msas_fft_rank}_{args.msas_top_sw}_{args.msas_top_sw_affine}"
    local_cache_folder = f"{0}_{args.msas_num}_{args.msas_top_fft}_{args.msas_fft_rank}_{args.msas_top_sw}_{args.msas_top_sw_affine}"
    assert args.chunks == 80, "Do not support controling this from CLI yet;  MSA is pre-loaded to pinned RAM."

    #print(files)

    #pbar = tqdm(files[::-1])
    pbar = tqdm(files)
    for c,p in enumerate(pbar):

        # handle single file vs folder. 
        if args.s3 != '': 
            s3_path = path + p.split('/')[-1].replace('.fasta', '.zip')
        else: 
            parts = p.split('/')
            if len(parts)>1:
                middle = ["foldify_" + parts[-2]] if args.output == '' else [args.output]
                path = parts[:-2] + middle + [parts[-1].replace('.fasta', '')]
                path = "/".join(path) + '/'
            else: 
                path = p.replace('.fasta', '')

        try: 
            skip = False 


            p = str(p)
            #content = open(p).read()
            content = fs.open(p, "rt").read()

            num_tokens = sum([len(line) for line in content.split('\n') if not line.startswith('>')])

            proteins = []
            for line in content.split('\n'):
                if line.startswith('>'): continue 
                if line == '': continue 
                if get_type(line) == 'SMILES': 
                    if not test(line): 
                        print(f"Skipping {p}. RDKit didn't like {line}. ")
                        #open(new_path, 'w').write(f"Skipping {p}. RDKit didn't like {line}. ")
                        skip = True 
                    else: 
                        #print('ok')
                        pass
                if get_type(line) == 'protein': proteins.append(line)
            if skip: continue 
            encoded = urllib.parse.quote(content, safe="")
            if len(content) == 0: continue 

            # Load msa from s3 
            if args.msa_s3:
                os.makedirs(f"sseqs/sseqs/cache_msa/{cache_folder}/", exist_ok=True)
                os.makedirs(f"sseqs/sseqs/cache_msa/{local_cache_folder}/", exist_ok=True)

                for protein in proteins:
                    protein_hash = hashlib.sha256(protein.encode('utf-8')).hexdigest()
                    pth = f"sseqs/sseqs/cache_msa/{cache_folder}/{protein_hash}.a3m"
                    local_pth = f"sseqs/sseqs/cache_msa/{local_cache_folder}/{protein_hash}.a3m"

                    src_path = f"{args.input[5:].split('/')[0]}/{cache_folder}/{protein_hash}.a3m"
                    dst= open(pth, 'w')
                    local_dst= open(local_pth, 'w')
                    with fs.open(src_path, 'r') as src:
                        s = src.read() 
                        dst.write(s)
                        local_dst.write(s)
                # [ ] could have a preload or asynch load of all;  probably adds ~1s or so to load.
                # e.g. `continue` here`

            # compute msa and store on s3
            elif args.msa_s3_precompute != '':
                # [ ] generalize this; the arguments s
                need_to_compute_msa = False
                for protein in proteins: 
                    protein_hash = hashlib.sha256(protein.encode('utf-8')).hexdigest()
                    if not fs.exists(f"{args.input[5:].split('/')[0]}/{cache_folder}/{protein_hash}.a3m"): 
                        need_to_compute_msa = True

                # already did this one skip it. 
                if not need_to_compute_msa: 
                    continue 

            # [ ] refactor so args dict is cast to URL. 
            url = f"{args.host}/fold?ui=False&seq={encoded}&gpu={args.gpu}&msas_num={args.msas_num}&msas_top_fft={args.msas_top_fft}&msas_fft_rank={args.msas_fft_rank}&msas_top_sw={args.msas_top_sw}&msas_top_sw_affine={args.msas_top_sw_affine}&diffusion_samples={args.diffusion_samples}"
            if args.msa_s3_precompute: url += "&return_only_msa=True"
            else: url += f"&get_msa_from_server={args.msa}&only_return_zip=True"

            # Open connection with progress reporting
            response = urllib.request.urlopen(url)
            block_size = 1024
            
            result = ''
            while True:
                data = response.read(block_size)
                if not data:
                    break
                result += data.decode('utf-8')
                pbar.set_description(f"{logo} {time.strftime('%H:%M:%S')} {p} tokens={num_tokens} {len(result)/1000}KB")

            jsons = [json.loads(a) for a in result.split('\n@\n') if a != '']

            if args.msa_s3_precompute: 
                # write the MSA cache one place?
                for j in jsons: 
                    if j['type'] == 'data_msa':
                        for k,v in j['data'].items():
                            # [ ] refactor hash / folder location to be from foldify and use that in backend
                            os.makedirs(f"sseqs/sseqs/cache_msa/{cache_folder}/", exist_ok=True)
                            content = v
                            protein = v.split(">original_query\n")[1].split("\n")[0]
                            protein_hash = hashlib.sha256(protein.encode('utf-8')).hexdigest()
                            pth = f"sseqs/sseqs/cache_msa/{cache_folder}/{protein_hash}.a3m"
                            open(pth, 'w'). write(content) 
                            with fs.open(f"{args.input[5:].split('/')[0]}/{cache_folder}/{protein_hash}.a3m", 'w') as f:
                                f.write(content)


            else: 
                b64_zip_data = jsons[-1]['data']

                zip_bytes = base64.b64decode(b64_zip_data)
                zip_in_memory = io.BytesIO(zip_bytes)
                with zipfile.ZipFile(zip_in_memory, 'r') as zip_ref:
                    if mode == LOCAL: 
                        os.makedirs(path, exist_ok=True)
                        zip_ref.extractall(path) 

                    elif mode == S3: 
                        with fs.open(f"{s3_path}", 'wb') as f:
                            f.write(zip_bytes)

        except Exception as e: 
            print('something wrong', e)
            print(url)
            pass 

        print('')
        wait_on_server(args.host)


def main() -> None:  # pragma: no cover

    import argparse

    parser = argparse.ArgumentParser(description='Foldify.ai CLI', add_help=False)
    parser.add_argument('-input', '-i', type=str, help='')
    parser.add_argument('-args', type=str, help='')
    parser.add_argument('-logmd', action='store_true', help='Log with LogMD')
    #parser.add_argument('-host', '-h', type=str, default='https://gpu1.foldify.org', help='Host URL for Foldify API')
    parser.add_argument('-host', '-h', type=str, default='http://0.0.0.0:8000', help='Host URL for Foldify API')
    parser.add_argument('-output', '-o', type=str, default='', help='Output directory for results')
    parser.add_argument('-gpu', '-g', type=int, default=0, help='GPU')
    parser.add_argument('-y', action='store_true', help='Pre-accept using remote host. ')
    parser.add_argument('-s3', type=str, default='', help='S3 endpoint (developed for cloudflared to lower cost).')
    parser.add_argument('-override', action='store_true', help='Override existing files')
    parser.add_argument('-msa', type=str, default='', help='Get msa from other ip. ')

    parser.add_argument('-msa_s3_precompute', action='store_true', help='Precompute MSA and store to s3. ')
    parser.add_argument('-msa_s3', action="store_true", help='Load MSA from s3. ') # have one process pre-download, don't want to wait.

    #foldify -i s3://dmitrij/demo.fasta -msa_s3 80_1024_20_1 -s3 https://8a6ab2cee54f34a71f5a8d99e92da2d2.r2.cloudflarestorage.com

    parser.add_argument('-diffusion_samples', type=int, default=1, help='Number of boltz2 diffusion samples')
    parser.add_argument('-msas_num', type=int, default=1024, help='Number of rows in final MSA .a3m file.')
    parser.add_argument('-msas_fft_rank', type=int, default=1, help='Accuracy of MSA, larger is better. ')
    parser.add_argument('-msas_k', type=int, default=1, help='Accuracy of MSA, larger is better. ')
    parser.add_argument('-msas_top_fft', type=int, default=20, help='Pass on from FFT to smith-waterman (e.g. 20 => top 5%).')
    parser.add_argument('-msas_top_sw', type=int, default=20, help='Pass on from smith-waterman to affine. ')
    parser.add_argument('-msas_top_sw_affine', type=int, default=20, help='Pass on from batch to final sorting.')
    parser.add_argument('-chunks', type=int, default=80, help='Cannot change this. ')

    #-s3 https://8a6ab2cee54f34a71f5a8d99e92da2d2.r2.cloudflarestorage.com

    args = parser.parse_args()

    if args.host == 'https://gpu1.foldify.org' and not args.y:
        print("You didn't specify host. The default is a remote. ")
        print("Reply `REMOTE` if you want to send sequences. ")
        if input() != 'REMOTE': 
            print('Exiting.')
            exit()
        else: 
            print("Using remote host. ")
            print("You can skip this check with `foldify -y`")

    #if args.prepare_msa and args.s3 == '':
    #    print("Please pass in `-s3 https;//...endpoint..`, can't prepare MSAs on S3 without an endpoint. ")
    #    exit()

    fold(args)


if __name__ == "__main__":  # pragma: no cover
    sys.argv = ['foldifyai','cofactors/']
    main() 
