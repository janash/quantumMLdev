"""
rest.py
quantumML is 

Handles the primary functions
"""
from urllib.request import urlopen
import json
import urllib
import os
import io
import math
from pymatgen.core.structure import Structure
from ase.io import vasp
from dscribe.descriptors import SOAP
from pymatgen.io.vasp import Xdatcar, Oszicar
from sklearn.cluster import KMeans
import numpy as np

class MWRester(object):
    results = {}

    def __init__(self, api_key=None,
                 endpoint="http://materialsweb.org/rest/calculation/?"):
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = ""
        self.preamble = endpoint
        import requests
        self.session = requests.Session()
        self.session.headers = {"x-api-key": self.api_key}

    def __str__(self):
        return '%s' % self.results

    def _make_request(self, sub_url, payload=None, method="GET",
                      mp_decode=True):
        url = self.preamble + sub_url + "/" + self.api_key
        x = urlopen(url)

        response = self.session.get(url, verify=True)
        data = json.loads(response.text)
        return data

    def get_calculation(self, band_gap_range=None, formation_energy_range=None, elements=[], space_group_number=None,
                        dimension=None, crystal_system=None, name=None):
        '''
        Method to that queries materialsweb database and returns a list of dictionaries of calculations that
        fit the querries parameters. Additionally
        Parameters:
            band_gap_range (list): List of band gap range e.g. [min, max]
            formation_energy_range (list): List of formation energy range e.g. [min, max]
            elements (list): List of str of elements
            space_group_number (int): space group number
            dimension (int): dimension as int e.g. 1 2 3
            crystal_system (str): name of crystal system
            name (str): name of material e.g. MoS2
        Returns:
            results: List of results matching quire parameters
        '''

        suburl = ''
        if band_gap_range != None:
            suburl += 'band_gap_min=' + str(band_gap_range[0]) + '&band_gap_max=' + str(band_gap_range[-1]) + '&'
        if formation_energy_range != None:
            suburl += 'formation_energy_min=' + str(formation_energy_range[0]) + '&formation_ener_max=' + str(
                formation_energy_range[-1]) + '&'

        if (space_group_number != None):
            suburl += 'spacegroup_number=' + str(space_group_number) + '&'

        if (dimension != None):
            suburl += 'dimension=' + str(dimension) + '&'

        if (crystal_system != None):
            'lattice_system=' + str(crystal_system) + '&'
        self.results = self._make_request(suburl)['results']
        return self.results

    def as_pymatgen_struc(self):
        '''
        Method that converts results to list of pymatgen strucutures
        Returns:
             struc: List of pymatgen structures
        '''
        struc = []
        for c in self.results:
            urlp = ('http://' + c['path'][9:21] + '.org/' + c['path'][22:] + '/POSCAR')
            file = urllib.request.urlopen(urlp)
            poscar = ''
            for line in file:
                poscar += line.decode("utf-8")

            s = Structure.from_str(poscar, fmt='poscar')
            struc.append(s)

        return struc

if __name__ == "__main__":
    # Do something if this file is invoked on its own
    print(MWRester())
