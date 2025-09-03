 
def get_type(seq: str) -> str:
    # normalise
    seq = seq.strip().upper().replace(" ", "").replace("\n", "")
    if not seq:
        raise ValueError("Empty sequence")

    # 1) quick SMILES test
    smiles_chars = set("[]=#@()+-\\/0123456789%")
    if any(c in smiles_chars for c in seq):
        return "SMILES"

    # 2) protein vs nucleic acid
    protein_letters = set("ACDEFGHIKLMNPQRSTVWYBXZJUO")   # AA + ambiguous codes
    dna_letters     = set("ACGTN")
    rna_letters     = set("ACGUN")

    letters_in_seq = set(seq)

    # anything outside nucleic-acid letters ⇒ protein
    if letters_in_seq - (dna_letters | rna_letters):
        return "protein"

    # only nucleic-acid letters left
    if 'U' in letters_in_seq and 'T' not in letters_in_seq:
        return "RNA"
    return "DNA"



def file_exists(s3_client, bucket, key):
    """ Checks if a file exists in an S3-compatible bucket.  """
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except:
        return False