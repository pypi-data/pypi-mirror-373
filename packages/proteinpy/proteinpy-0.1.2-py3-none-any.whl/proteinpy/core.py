import requests # type: ignore
import re
import json
import csv
import matplotlib.pyplot as plt # type: ignore
from collections import Counter

class Protein:
    BASE_URL = "https://rest.uniprot.org/uniprotkb"

    def __init__(self, uniprot_id):
        self.uniprot_id = uniprot_id
        self._header = None
        self._sequence = None
        self._length = None
        self._fetched = False

    def fetch(self):
        url = f"{self.BASE_URL}/{self.uniprot_id}.fasta"
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Could not fetch UniProt ID: {self.uniprot_id}")
        lines = response.text.strip().split('\n')
        self._header = lines[0][1:]
        self._sequence = ''.join(lines[1:])
        self._length = len(self._sequence)
        self._fetched = True

    def read(self):
        if not self._fetched:
            self.fetch()
        return self._header, self._sequence, self._length

    def write(self, file_path):
        if not self._fetched:
            self.fetch()
        with open(file_path, 'w') as f:
            f.write(f">{self._header}\n")
            for i in range(0, self._length, 60):
                f.write(self._sequence[i:i+60] + '\n')

    def print(self):
        if not self._fetched:
            self.fetch()
        print(f">{self._header}\n{self._sequence}\nLength: {self._length}")

    def aa_counts(self):
        if not self._fetched:
            self.fetch()
        return dict(Counter(self._sequence))

    def mol_weight(self):
        if not self._fetched:
            self.fetch()
        aa_weights = {
            'A': 89.09,  'R': 174.20, 'N': 132.12, 'D': 133.10, 'C': 121.15,
            'Q': 146.15, 'E': 147.13, 'G': 75.07,  'H': 155.16, 'I': 131.17,
            'L': 131.17, 'K': 146.19, 'M': 149.21, 'F': 165.19, 'P': 115.13,
            'S': 105.09, 'T': 119.12, 'W': 204.23, 'Y': 181.19, 'V': 117.15
        }
        return round(sum(aa_weights.get(aa, 0.0) for aa in self._sequence), 2)

    def iso_point(self):
        if not self._fetched:
            self.fetch()
        positive = sum(self._sequence.count(aa) for aa in 'KRH')
        negative = sum(self._sequence.count(aa) for aa in 'DEY')
        return round((7 + (positive - negative) * 0.1), 2)

    def gravy(self):
        if not self._fetched:
            self.fetch()
        hydropathy = {
            'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5,
            'Q': -3.5, 'E': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5,
            'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6,
            'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2
        }
        total = sum(hydropathy.get(aa, 0) for aa in self._sequence)
        return round(total / self._length, 3)

    def aromaticity(self):
        if not self._fetched:
            self.fetch()
        aromatics = sum(self._sequence.count(aa) for aa in 'FYW')
        return round(aromatics / self._length, 3)

    def aliphatic_index(self):
        if not self._fetched:
            self.fetch()
        counts = Counter(self._sequence)
        ai = (
            100 * (counts['A'] + 2.9 * counts['V'] +
                   3.9 * (counts['I'] + counts['L'])) / self._length
        )
        return round(ai, 2)

    def subseq(self, start, end):
        if not self._fetched:
            self.fetch()
        return self._sequence[start - 1:end]

    def kmers(self, k):
        if not self._fetched:
            self.fetch()
        return [self._sequence[i:i+k] for i in range(len(self._sequence) - k + 1)]

    def mutate(self, position, new_aa):
        if not self._fetched:
            self.fetch()
        if position < 1 or position > self._length:
            raise IndexError("Position out of bounds")
        return self._sequence[:position-1] + new_aa + self._sequence[position:]

    def multi_mutate(self, mutations):
        if not self._fetched:
            self.fetch()
        seq = list(self._sequence)
        for pos, aa in mutations:
            if pos < 1 or pos > self._length:
                raise IndexError(f"Position {pos} out of bounds")
            seq[pos - 1] = aa
        return ''.join(seq)


    def to_dict(self):
        if not self._fetched:
            self.fetch()
        return {
            "id": self.uniprot_id,
            "header": self._header,
            "sequence": self._sequence,
            "length": self._length,
            "molecular_weight": self.mol_weight(),
            "gravy": self.gravy(),
            "aromaticity": self.aromaticity(),
            "aliphatic_index": self.aliphatic_index()
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)

    def to_csv(self, file_path):
        data = self.to_dict()
        with open(file_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            writer.writeheader()
            writer.writerow(data)


    def aa_distribution(self):
        if not self._fetched:
            self.fetch()
        counts = self.aa_counts()
        plt.figure(figsize=(10, 5))
        plt.bar(counts.keys(), counts.values())
        plt.title(f"Amino Acid Distribution - {self.uniprot_id}")
        plt.xlabel("Amino Acid")
        plt.ylabel("Frequency")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.show()

    def find_motif(self, pattern):
        if not self._fetched:
            self.fetch()
        return [m.start() + 1 for m in re.finditer(pattern, self._sequence)]



    def summary(self):
        if not self._fetched:
            self.fetch()
        print(f"Protein ID: {self.uniprot_id}")
        print(f"Header: {self._header}")
        print(f"Length: {self._length} residues")
        print(f"Molecular Weight: {self.mol_weight()} Da")
        print(f"Isoelectric Point (approx): {self.iso_point()}")
        print(f"GRAVY Score: {self.gravy()}")
        print(f"Aromaticity: {self.aromaticity()}")
        print(f"Aliphatic Index: {self.aliphatic_index()}")



