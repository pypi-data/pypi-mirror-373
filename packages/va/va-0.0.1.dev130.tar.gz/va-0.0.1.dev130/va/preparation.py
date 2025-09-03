"""

preparation.py

preparation class is used to initialize the input and working
environment for validation analysis.

Copyright [2013] EMBL - European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the
"License"); you may not use this file except in
compliance with the License. You may obtain a copy of
the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. See the License for the
specific language governing permissions and limitations
under the License.

"""

__author__ = 'Zhe Wang'
__email__ = 'zhe@ebi.ac.uk'
__date__ = '2018-07-24'


import os
import sys
import psutil
import re
import codecs
import timeit
import json
import glob
import argparse
import traceback
import mrcfile
import numpy as np
import xml.etree.ElementTree as ET
import copy
from PIL import Image
from Bio.PDB import MMCIFParser
from Bio.PDB.mmcifio import MMCIFIO
from Bio.PDB.PDBIO import Select
from Bio.PDB.MMCIF2Dict import MMCIF2Dict

from va.utils.Checker import feature_assessment
# from emda.core import iotools
# from emda import emda_methods
from va.validationanalysis import ValidationAnalysis
from va.version import __version__
from va.utils.misc import out_json
from memory_profiler import profile

try:
    from PATHS import MAP_SERVER_PATH
    from PATHS import THREEDFSC_ROOT
    from PATHS import LIB_STRUDEL_ROOT
except ImportError:
    MAP_SERVER_PATH = None
    THREEDFSC_ROOT = None
    LIB_STRUDEL_ROOT = None


class NotDisordered(Select):
    """
    Selects non-disordered atoms from a Biopython structure instance.

    Methods:
        accept_atom(atom): Returns True if the atom is not disordered or has altloc "A", otherwise False.

    Example:
        selector = NotDisordered()
        io.save(filename, select=selector)
    """

    def accept_atom(self, atom):
        """
        Determines if an atom should be accepted based on disorder status and altloc.

        Args:
            atom (Bio.PDB.Atom.Atom): Atom instance from Biopython.

        Returns:
            bool: True if the atom is not disordered or has altloc "A", False otherwise.
        """
        if (not atom.is_disordered()) or atom.get_altloc() == "A":
            atom.set_altloc(" ")
            return True
        else:
            return False


class PreParation:

    def __init__(self):
        """
            Initialization of objects for Validation analysis
        """
        self.args = self.read_para()
        self.emdid = self.args.emdid
        self.json = self.args.j
        methoddict = {'tomography': 'tomo', 'twodcrystal': 'crys', 'singleparticle': 'sp',
                      'subtomogramaveraging': 'subtomo', 'helical': 'heli', 'crystallography': 'crys',
                      'single particle': 'sp', 'subtomogram averaging': 'subtomo'}
        if self.emdid:
            self.mapname = 'emd_{}.map'.format(self.emdid)
            self.subdir = self.folders(self.emdid)
            self.dir = '{}{}/va/'.format(MAP_SERVER_PATH, self.subdir)
            filepath = '{}{}/va/{}'.format(MAP_SERVER_PATH, self.subdir, self.mapname)
            try:
                inputdict = self.read_header()
                if os.path.isfile(filepath):
                    # Read header file
                    inputdict = self.read_header()
                    self.model = inputdict['fitmodels']
                    self.contourlevel = inputdict['reccl']
                    if len(inputdict['halfmaps']) == 2:
                        self.evenmap = inputdict['halfmaps'][0]
                        self.oddmap = inputdict['halfmaps'][1]
                    else:
                        self.evenmap = None
                        self.oddmap = None
                    self.pid = inputdict['fitpid']
                self.method = (inputdict['method']).lower()
                self.resolution = inputdict['resolution']
                self.masks = inputdict['masks'] if inputdict['masks'] is not None else self.collectmasks()
                self.modelmap = self.args.modelmap
                self.mofit_libpath = LIB_STRUDEL_ROOT
                self.threedfscdir = THREEDFSC_ROOT
                self.onlybar = self.args.onlybar
            except:
                print('No proper header information.')


            self.run = self.args.run
            if any(x in ['rmmcc', 'mmfsc'] for x in self.run):
                self.modelmap = True
            self.fscfile = self.findfscxml()
            self.platform = 'emdb'
            if self.args.p in ['emdb', 'wwpdb']:
                self.platform = self.args.p
            else:
                print('Please use "emdb" or "wwpdb" as platform argument.')
            self.update_resolution_bin_file = self.args.update_resolution_bin_file

        elif self.json:
            self.mapname, self.dir, self.model, self.contourlevel, self.evenmap, self.oddmap, \
            self.fscfile, self.method, self.resolution, self.masks, self.run, self.platform, \
            self.modelmap, self.onlybar, self.update_resolution_bin_file, self.threedfscdir, self.mofit_libpath = self.read_json(self.json)
            self.method = methoddict[self.method.lower()] if self.method is not None else None

        else:

            if self.args.positions is None:
                self.mapname = self.args.m
                self.model = self.args.f
                self.pid = self.args.pid
                self.emdid = self.args.emdid
                self.evenmap = self.args.hmeven
                self.oddmap = self.args.hmodd
                self.contourlevel = self.read_contour()
                self.run = self.args.run
                self.dir = self.args.d + '/'
                self.method = methoddict[self.args.met.lower()] if self.args.met is not None else None
                self.resolution = self.args.s
                self.platform = 'emdb'
                if self.args.p in ['emdb', 'wwpdb']:
                    self.platform = self.args.p
                else:
                    print('Please use "emdb" or "wwpdb" as platform argument.')

                if self.args.ms is not None:
                    self.masks = {self.dir + i: float(j) for i, j in zip(self.args.ms, self.args.mscl)}
                else:
                    self.masks = {}
                self.fscfile = self.findfscxml()
                self.modelmap = True if self.args.modelmap else False
                self.onlybar = True if self.args.onlybar else False
                self.threedfscdir = self.args.threeddir if self.args.threeddir else None
                self.mofit_libpath = self.args.strdlib if self.args.strdlib else None
                self.update_resolution_bin_file = self.args.update_resolution_bin_file if self.args.update_resolution_bin_file else None
            else:
                if self.args.positions == 'strudel':
                    self.full_modelpath = self.args.strdmodel
                    self.full_mappath = self.args.strdmap
                    self.mofit_libpath = self.args.strdlib
                    self.strdout = self.args.strdout
                    self.dir = self.args.strdout


    def findfscxml(self):
        """
            Find the fsc.xml file if exist
        :return:
        """

        fscxmlre = '*_fsc.xml'
        fscxmlarr = glob.glob(self.dir + fscxmlre)
        if not fscxmlarr:
            print('No fsc.xml file can be read for FSC information.')
            return None
        elif len(fscxmlarr) > 1:
            print('There are more than one FSC files in the folder. Please make sure only one exist.')
            return None
        else:
            filefsc = os.path.basename(fscxmlarr[0])
            return filefsc

    def read_json(self, injson):
        """
            Load input arguments from JSON file
        :return: dictionary which contains corresponding parameters for the pipeline
        """

        if injson:
            with open(injson, 'r') as f:
                args = json.load(f)
            argsdata = args['inputs']
            map = argsdata['map']
            assert map is not None, "There must be a map needed in the input JSON file."
            assert argsdata['workdir'] is not None, "Working directory must be provided in the input JSON file."
            workdir = str(argsdata['workdir'] + '/')
            if 'contour_level' in argsdata and argsdata['contour_level'] is not None:
                # cl = argsdata['contour_level']
                cl = ("%.12f" % argsdata['contour_level']).rstrip('0').rstrip('.')
            else:
                print('There is no contour level.')
                cl = None

            if 'evenmap' in argsdata and argsdata['evenmap'] is not None:
                evenmap = argsdata['evenmap']
            else:
                print('There is no evnemap.')
                evenmap = None

            if 'oddmap' in argsdata and argsdata['oddmap'] is not None:
                oddmap = argsdata['oddmap']
            else:
                print('There is no oddmap.')
                oddmap = None

            if 'fscfile' in argsdata and argsdata['fscfile'] is not None:
                fscfile = argsdata['fscfile']
            else:
                print('There is no fsc file.')
                fscfile = None

            if 'method' in argsdata and argsdata['method'] is not None:
                method = argsdata['method']
            else:
                print('There is no method information.')
                method = None

            if 'resolution' in argsdata and argsdata['resolution'] is not None:
                resolution = argsdata['resolution']
            else:
                print('There is no resolution information.')
                resolution = None

            if 'runs' in argsdata and argsdata['runs'] is not None:
                runs = argsdata['runs']
            else:
                runs = 'all'

            if 'models' in argsdata and argsdata['models'] is not None:
                models = [argsdata['models'][item]['name'] for item in argsdata['models'] if item is not None]
            else:
                models = None

            if 'masks' in argsdata and argsdata['masks'] is not None:
                masks = {workdir + argsdata['masks'][item]['name']: argsdata['masks'][item]['contour']
                          for item in argsdata['masks']}
            else:
                masks = {}

            if 'platform' in argsdata and argsdata['platform'] in ['emdb', 'wwpdb']:
                platform = str(argsdata['platform'])
            else:
                print('There is no platform information.')
                platform = 'emdb'

            if 'modelmap' in argsdata and argsdata['modelmap'] == 1:
                modelmap = True
            else:
                modelmap = False
                print('Model map and related calculations will not be done. Please specify modelmap in input json.')

            if 'onlybar' in argsdata and argsdata['onlybar'] == 1:
                onlybar = True
            else:
                onlybar = False

            if 'update_resolution_bin_file' in argsdata and argsdata['update_resolution_bin_file'] is not None:
                update_resolution_bin_file = argsdata['update_resolution_bin_file']
            else:
                update_resolution_bin_file = None

            if '3dfscdir' in argsdata and argsdata['3dfscdir'] is not None:
                threedfscdir = argsdata['3dfscdir']
            else:
                print('There is no 3dfsc directory information.')
                threedfscdir = None

            if 'strudellib' in argsdata and argsdata['strudellib'] is not None:
                mofit_libpath = argsdata['strudellib']
            else:
                print('There is no 3dfsc directory information.')
                mofit_libpath = None

            return (map, workdir, models, cl, evenmap, oddmap, fscfile,
                    method, resolution, masks, runs, platform, modelmap,
                    onlybar, update_resolution_bin_file, threedfscdir, mofit_libpath)
        else:
            print('Input JSON needed.')

    def runs(self):
        """
            Check parameters for -run
        :return: dictionary contains binary value of each parameter of -run
        """

        # If only one argument, it will be string type and should be converted to lower letters directly
        # For more than one arguments, it will be list type
        if isinstance(self.run, str):
            runs = self.run.lower()
        else:
            runs = [x.lower() for x in self.run]
        if runs[0] == 'validation':
            return ['projection', 'central', 'surface', 'volume', 'density', 'raps', 'largestvariance', 'mask',
                    'inclusion', 'fsc', 'qscore']
                    # 'smoc', 'resccc', 'resmap']
        else:
            resdict = {'all': False, 'projection': False, 'central': False, 'surface': False, 'density': False,
                       'volume': False, 'fsc': False, 'raps': False, 'mapmodel': False, 'inclusion': False,
                       'largestvariance': False, 'mask': False, 'symmetry': False, 'rmmcc': False, 'smoc': False,
                       'resccc': False, 'emringer': False, 'strudel': False, '3dfsc': False, 'resmap': False}
            for key in resdict.keys():
                if key in runs:
                    resdict[key] = True
            # If -run has arguments but do not fit with any above, set to all to True
            if True not in resdict.values():
                resdict['all'] = False

            runlist = []

            # not for OneDep for now: mmfsc, symmetry, qscore, some projectioins
            if self.mapname is not None:
                runlist.extend(['projection', 'central', 'surface', 'volume', 'density', 'raps', 'largestvariance',
                                'mask', 'fsc', 'mmfsc', 'rmmcc', 'symmetry', 'qscore', 'strudel', 'emringer', '3dfsc',
                                'smoc', 'resccc', 'resmap'
                                ])

            if self.masks is None:
                runlist.remove('mask')

            if self.model is not None and self.contourlevel is not None:
                runlist.extend(['inclusion'])
            else:
                sys.stderr.write('REMINDER: Contour level or model needed for atom and residue inclusion.\n')

            if runs[0] == 'all' or runs == 'all':
                finallist = runlist
            else:
                finallist = list(set(runlist) & set(runs))

            return finallist


    @staticmethod
    def folders(emdid):
        """

            Folders' path for the one entry with its ids

        :return: Dictionary key: id value: subpath of that entry
        """


        breakdigits = 2
        emdbidmin = 4
        if len(emdid) >= emdbidmin and isinstance(emdid, str):
            topsubpath = emdid[:breakdigits]
            middlesubpath = emdid[breakdigits:-breakdigits]
            subpath = os.path.join(topsubpath, middlesubpath, emdid)

            return subpath
        else:
            return None


    def read_header(self):
        """
            Correspoding to Heder file version 3.0
            When "-emdid" is give, we search the input information for validation analysis
            inside the header file and return a dictionary

        :return:
        """

        headerfile = '{}{}/va/emd-{}.xml'.format(MAP_SERVER_PATH, self.subdir, self.emdid)
        headerdict = {}
        if os.path.isfile(headerfile):
            tree = ET.parse(headerfile)
            root = tree.getroot()

            # Model
            fitmodel = []
            fitpid = []
            for model in tree.findall('./crossreferences/pdb_list/pdb_reference/pdb_id'):
                fitmodel.append(model.text.lower() + '.cif')
                fitpid.append(model.text.lower())

            # contour
            contour_list = []
            for contour in tree.findall('./map/contour_list/contour/level'):
                contour_list.append(contour.text.lower())
            reccl = None
            if contour_list:
                #reccl = "{0:.3f}".format(float(contour_list[0]))
                reccl = float(contour_list[0])

            # Half maps
            halfmapsfolder = '{}{}/va/*_half_map_*.map'.format(MAP_SERVER_PATH, self.subdir)
            halfmaps = glob.glob(halfmapsfolder)

            # check when there is fitted models for tomography data, do not count the fitted model
            # for calculating atom inclusion, residue inclusion or map model view
            structure_determination_list = root.find('structure_determination_list')
            structure_determination = structure_determination_list.find('structure_determination') if structure_determination_list else None
            cur_method = structure_determination.find('method') if structure_determination else None
            method = cur_method.text if not cur_method else None
            headerdict['fitmodels'] = None if method == 'tomography' else fitmodel

            # Resolution
            all_processings = {
                'singleParticle': 'singleparticle',
                'subtomogramAveraging': 'subtomogram_averaging',
                'tomography': 'tomography',
                'electronCrystallography': 'crystallography',
                'helical': 'helical'
            }
            processing = all_processings[method] if method else None
            cur_processing = '{}_processing'.format(processing) if processing else None
            tres = structure_determination.find('./{}/final_reconstruction/resolution'.format(cur_processing))
            resolution = tres.text if tres is not None else None

            # Masks
            masks = {}
            for model in tree.findall('./interpretation/segmentation_list/segmentation/file'):
                # masks.append(self.dir + child.find('file').text)
                # Here as there is no mask value from the header, I use 1.0 for all masks
                masks[self.dir + model.text.lower()] = 1.0

            methoddict = {'tomography': 'tomo', 'electronCrystallography': '2dcrys', 'singleParticle': 'sp',
                          'subtomogramAveraging': 'subtomo', 'helical': 'heli'}

            headerdict['fitmodels'] = fitmodel if fitmodel else None
            headerdict['fitpid'] = fitpid
            headerdict['reccl'] = reccl
            headerdict['halfmaps'] = halfmaps
            headerdict['method'] = methoddict[method]
            headerdict['resolution'] = resolution
            headerdict['masks'] = masks if masks else None


            return headerdict

        else:
            print('Header file: %s does not exit.' % headerfile)
            raise OSError('Header file does not exist.')

    def read_header_old(self):
        """

            When "-emdid" is give, we search the input information for validation analysis
            inside the header file and return a dictionary

        :return:
        """

        headerfile = '{}{}/va/emd-{}.xml'.format(MAP_SERVER_PATH, self.subdir, self.emdid)
        headerdict = {}
        if os.path.isfile(headerfile):
            tree = ET.parse(headerfile)
            root = tree.getroot()

            # Fitted models
            deposition = root.find('deposition')
            fitlist = deposition.find('fittedPDBEntryIdList')
            fitmodel = []
            fitpid = []
            if fitlist is not None:
                for child in fitlist.iter('fittedPDBEntryId'):
                    fitmodel.append(child.text + '.cif')
                    fitpid.append(child.text)

            # Recommended contour level
            map = root.find('map')
            contourtf = map.find('contourLevel')
            reccl = None
            if contourtf is not None:
                reccl = "{0:.3f}".format(float(map.find('contourLevel').text))

            # Half maps
            halfmapsfolder = '{}{}/va/*_half_map_*.map'.format(MAP_SERVER_PATH, self.subdir)
            halfmaps = glob.glob(halfmapsfolder)

            # check when there is fitted models for tomography data, do not count the fitted model
            # for calculating atom inclusion, residue inclusion or map model view
            processing = root.find('processing')
            method = processing.find('method').text
            headerdict['fitmodels'] = None if method == 'tomography' else fitmodel


            # Got the resolution value from the header
            reconstruction = processing.find('reconstruction')
            preresolution = reconstruction.find('resolutionByAuthor')
            if preresolution is None:
                resolution = None
            else:
                resolution = preresolution.text


            # Masks
            supplement = root.find('supplement')
            maskset = supplement.find('maskSet') if supplement is not None else None
            masks = {}
            if maskset is not None:
                for child in maskset.iter('mask'):
                    # masks.append(self.dir + child.find('file').text)
                    # Here as there is no mask value from the header, I use 1.0 for all masks
                    masks[self.dir + child.find('file').text] = 1.0
            methoddict = {'tomography': 'tomo', 'twoDCrystal': '2dcrys', 'singleParticle': 'sp',
                          'subtomogramAveraging': 'subtomo', 'helical': 'heli'}

            headerdict['fitmodels'] = fitmodel if fitmodel else None
            headerdict['fitpid'] = fitpid
            headerdict['reccl'] = reccl
            headerdict['halfmaps'] = halfmaps
            headerdict['method'] = methoddict[method]
            headerdict['resolution'] = resolution
            headerdict['masks'] = masks if masks else None


            return headerdict

        else:
            print('Header file: %s does not exit.' % headerfile)
            raise OSError('Header file does not exist.')

    @staticmethod
    def str2bool(arg_input):
        """
            Method that make input to bool type used in arg parser 'type'

        :param arg_input:
        :return:
        """
        if isinstance(arg_input, bool):
            return arg_input
        if arg_input.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif arg_input.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected')

    @staticmethod
    def read_para():
        """

            Read arguments


        """

        assert len(sys.argv) > 1, ('There has to be arguments for the command.\n \
               Usage: mainva.py [-h] -m [M] -d [D] [-f [F]] [-pid [PID]] [-hm [HM]] [-cl [CL]]\n \
               or:    mainva.py -emdid <EMDID>\n \
               or:    mainva.py -j <input.json>')
        methodchoices = ['tomography', 'twodcrystal', 'crystallography', 'singleparticle', 'single particle',
                         'subtomogramaveraging', 'subtomogram averaging', 'helical']

        parser = argparse.ArgumentParser(description='Input density map(name) for Validation Analysis')
        #parser = mainparser.add_mutually_exclusive_group(required = True)
        parser.add_argument('--version', '-V', action='version', version='va: {version}'.format(version=__version__),
                            help='Version')
        parser.add_argument('-f', nargs='*',
                            help='Structure model file names. Multiple model names can be used with space separated.')
        parser.add_argument('-pid', nargs='?', help='PDB ID which needed while "-f" in use.')
        parser.add_argument('-hmeven', nargs='?', help='Half map.')
        parser.add_argument('-hmodd', nargs='?', help='The other half map.')
        parser.add_argument('-cl', nargs='?', help='The recommended contour level .')
        parser.add_argument('-run', nargs='*', help='Run customized validation analysis.', default='all')
        parser.add_argument('-met', nargs='?', help='EM method: tomography-tomo, twoDCrystal-2dcrys, singleParticle-sp, '
                                                    'subtomogramAveraging-subtomo, helical-heli', choices=methodchoices)
        parser.add_argument('-s', nargs='?', help='Resolution of the map.')
        parser.add_argument('-ms', nargs='*', help='All masks')
        parser.add_argument('-mscl', nargs='*', help='Contour level corresponding to the masks.')
        parser.add_argument('-p', nargs='?', type=str, help='Platform to run the data either wwpdb or emdb', default='emdb')
        parser.add_argument('-i', '--modelmap', type=PreParation.str2bool,
                            help='If specified then model map will be produce or vice versa', default=False)
        parser.add_argument('-b', '--onlybar', dest='onlybar', type=PreParation.str2bool,
                            help='If specified then only produce bar instead of running actual metric', default=False)
        parser.add_argument('--strdlib', nargs='?', help='Strudel library path')
        parser.add_argument('--threeddir', '-threedd', nargs='?', type=str, help='3DFSC root directory')
        parser.add_argument(
            '-u', '--update_resolution_bin_file',
            dest='update_resolution_bin_file',
            type=str,
            default=None,
            help='Full path to a CSV file for updating resolution bin for Q-score'
        )
        requiredname = parser.add_argument_group('required arguments')
        requiredname2 = parser.add_argument_group('alternative required arguments')
        requiredname3 = parser.add_argument_group('alternative required arguments')
        # requiredname_strudel = parser.add_argument_group('Strudel calculation arguments')
        requiredname.add_argument('-m', nargs='?', help='Density map file')
        requiredname.add_argument('-d', nargs='?', help='Directory of all input files')
        # requiredname_strudel.add_argument('strudel', nargs='?', help='Strudel calculation')
        requiredname2.add_argument('-emdid', nargs='?', help='EMD ID with which can run without other parameters.')
        requiredname3.add_argument('-j', nargs='?', help='JSON file which has all arguments.')
        # requiredname_strudel.add_argument('--strdmodel', nargs='?', help='Strudel model path')
        # requiredname_strudel.add_argument('--strdmap', nargs='?', help='Strudel map path')
        # requiredname_strudel.add_argument('--strdlib', nargs='?', help='Strudel library path')

        subparser = parser.add_subparsers(dest='positions')
        pstrudel = subparser.add_parser('strudel', description='Calculation of Strudel')
        pstrudel.add_argument('-p', '--strdmodel', nargs='?', help='Strudel model path')
        pstrudel.add_argument('-m', '--strdmap', nargs='?', help='Strudel map path')
        pstrudel.add_argument('-l', '--strdlib', nargs='?', help='Strudel library path')
        pstrudel.add_argument('-d', '--strdout', nargs='?', help='Strudel output path')


        presmap = subparser.add_parser('resmap', description='Calculation of local resolution with ResMap')
        presmap.add_argument('-o', '--oddmap', nargs='?', help='Full path to oddmap')
        presmap.add_argument('-e', '--evemap', nargs='?', help='Full path to evenmap')
        presmap.add_argument('-s', '--resmap', nargs='?', help='Full path to ResMap.py')

        args = parser.parse_args()

        checkpar = (isinstance(args.m, type(None)) and isinstance(args.f, type(None)) and
                    isinstance(args.pid, type(None)) and isinstance(args.hmeven, type(None)) and
                    isinstance(args.cl, type(None)) and isinstance(args.hmodd, type(None)) and
                    isinstance(args.emdid, type(None)) and isinstance(args.run, type(None)) and
                    isinstance(args.j, type(None)) and isinstance(args.ms, type(None)) and
                    isinstance(args.mscl, type(None)) and isinstance(args.p, type(None)) and
                    isinstance(args.modelmap, type(None)))

        if checkpar:
            print('There has to be arguments for the command. \n \
                  usage: mainva.py [-h] [-m [M]] [-d [D]] [-f [F]] [-pid [PID]] [-hm [HM]] [-cl [CL]]'
                  '[-i/--modelmap] [-run [all]/[central...]]\n \
                  or   : mainva.py [-emdid [EMDID]] [-run [-run [all]/[central...]]] \n \
                  or   : mainva.py [-j] <input.json>\n \
                  or   : mainva.py strudel [-p/--strdmodel] <fullmodelpath> [-m/strdmap] <fullmappath>\n \
                                            [-l/--strdlib] <Strudel library path> [-d/--strdout] <Strudel output path>')
            sys.exit()
        return args

    def mrccheck(self, input_file):
        """
            Test if the file is an mrc file

        :param input: a string of full file name
        :return: a string of file name
        """

        try:

            a = mrcfile.mmap(input_file)
            return True
        except ValueError as e:

            print('File {} is not a mrc file.'.format(input_file))
            return False


    def collectmasks(self):
        """
            todo: Collect masks information if exist return list of mask with full path
            else None(This can be used for unittest, here as the each masks need to corresponding to a contour level
            so the masks' full path and its corresponding contour level need to be generated by reading mmcif file
            and put into a dictionary.

        :return:
        """
        search_mask = []
        reg = re.compile(r'(.*?)_(mask|msk)(.*?)\.map')

        for root, _, files in os.walk(self.dir):
            for file in files:
                if 'binarized' in file or 'masked' in file:
                    continue
                if reg.match(file) and self.mrccheck(os.path.join(self.dir, file)):
                    search_mask.append(file)

        if search_mask:
            print('!!! Be careful the masks were only taken from the folder instead of the header. Header missing the '
                  'corresponding information. For all masks we assume proper contour is 1.0')
            return {mask: 1.0 for mask in search_mask}

        return {}


    def read_contour(self):
        """

            If contour level is not offer,  we need either pid or emdid to get the recommended contour level info
            If contour level is not given by user, estimate a reasonable contour level (Todo)

        :return: contour level

        """

        if self.args.cl:
            return float(self.args.cl)
        else:
            # Todo: Add a estimated contour level function here
            return None


    # @profile
    def write_map(self, outmap_name, mapdata, nstarts, org_header):
        """
            When map axes permuted, make it normal and save the map

        :return:
        """

        # with mrcfile.new(outmap_name, overwrite=True) as mout:
        mout = mrcfile.new(outmap_name, overwrite=True)
        mout.set_data(mapdata)
        mout.update_header_from_data()
        mout.header.cella = org_header.cella
        mout.header.cellb = org_header.cellb

        mout.header.nxstart, mout.header.nystart, mout.header.nzstart = nstarts

        mout.header.mapc = 1
        mout.header.mapr = 2
        mout.header.maps = 3

        mout.header.mx = org_header.mx
        mout.header.my = org_header.my
        mout.header.mz = org_header.mz

        mout.header.origin.x = org_header.origin.x
        mout.header.origin.y = org_header.origin.y
        mout.header.origin.z = org_header.origin.z
        mout.header.label = org_header.label
        mout.flush()
        mout.close()


    # load map by using mrcfile
    # @profile
    def new_frommrc_totempy(self, fullmapname):
        """
            Transfer the mrcfile map object to TEMPy map object

        :param fullmapname: sgtring of primary map name
        :return: TEMPy map object
        """

        reload_map = None
        mrcmap = mrcfile.mmap(fullmapname, mode='r+')
        mrcheader = mrcmap.header
        datatype = mrcmap.data.dtype
        # mapdata = mrcmap.data.astype('float')
        mapdata = mrcmap.data
        crs = (mrcheader.mapc, mrcheader.mapr, mrcheader.maps)
        nstarts = (mrcheader.nxstart, mrcheader.nystart, mrcheader.nzstart)
        reversecrs = crs[::-1]
        stdcrs = (3, 2, 1)
        diffcrs = tuple(x-y for x, y in zip(reversecrs, stdcrs))
        if diffcrs != (0, 0, 0):

            aa = copy.deepcopy(mrcmap.header.mx)
            bb = copy.deepcopy(mrcmap.header.my)
            cc = copy.deepcopy(mrcmap.header.mz)

            crsindices = (crs.index(1), crs.index(2), crs.index(3))
            new_order = [2 - crsindices[2 - i] for i in (0, 1, 2)]
            mapdata = mapdata.transpose(new_order)
            nstarts = [mrcmap.header.nxstart, mrcmap.header.nystart, mrcmap.header.nzstart]

            x = copy.deepcopy(nstarts[crsindices[0]])
            y = copy.deepcopy(nstarts[crsindices[1]])
            z = copy.deepcopy(nstarts[crsindices[2]])

            output_map = fullmapname[:-4] + '_nonpermuted.map'
            self.write_map(output_map, mapdata, (x, y, z), mrcheader)
            mrcmap.close()
            reload_map = mrcfile.mmap(output_map, mode='r+')
            reload_map.fullname = fullmapname

        mrcmap.fullname = fullmapname
        return reload_map if reload_map else mrcmap

    # @profile
    def read_map(self):
        """
            Read maps
        """

        start = timeit.default_timer()

        try:
            if self.emdid:
                fullmapname = '{}{}/va/{}'.format(MAP_SERVER_PATH, self.subdir, self.mapname)
                mapsize = os.stat(fullmapname).st_size
                inputmap = self.new_frommrc_totempy(fullmapname)
                self.primarymapmean = inputmap.data.mean()
                self.primarymapstd = inputmap.data.std()
                nancheck = np.isnan(inputmap.data).any()
                assert not nancheck, 'There is NaN value in the map, please check.'
                mapdimension = inputmap.header.nx * inputmap.header.nx * inputmap.header.nx
                end = timeit.default_timer()

                print('Read map time: %s' % (end - start))
                print('------------------------------------')

                return inputmap, mapsize, mapdimension
            elif os.path.exists(self.dir) and self.mapname is not None:
                fullmapname = self.dir + self.mapname
                if not os.path.isfile(fullmapname):
                    fullmapname = self.mapname
                mapsize = os.stat(fullmapname).st_size
                # Swith off using the TEMPy to read map and using the mrcfile loaded information for reading map
                inputmap = self.new_frommrc_totempy(fullmapname)
                self.primarymapmean = inputmap.data.mean()
                self.primarymapstd = inputmap.data.std()
                nancheck = np.isnan(inputmap.data).any()
                nan_values = np.argwhere(np.isnan(inputmap.data))
                assert not nancheck, 'There is NaN value ({}) in the map, please check.'.format(nan_values)
                mapdimension = inputmap.header.nx * inputmap.header.nx * inputmap.header.nx

                end = timeit.default_timer()
                print('Read map time: %s' % (end - start))
                print('------------------------------------')

                return inputmap, mapsize, mapdimension
            else:
                print('------------------------------------')
                print('Folder: %s does not exist.' % self.dir)
                exit()
        except:
            print('Map does not exist or corrupted.')
            sys.stderr.write('Error: {} \n'.format(sys.exc_info()[1]))
            print('------------------------------------')
            exit()

    def remove_lines_after_match(self, input_file, output_file, match_text):
        try:
            with open(input_file, 'r') as infile:
                found_second_match = False
                match_count = 0
                content_before_second_match = []

                for line in infile:
                    if line.startswith(match_text):
                        match_count += 1
                        if match_count >= 2:
                            found_second_match = True
                            break
                    content_before_second_match.append(line)

            if found_second_match:
                with open(output_file, 'w') as outfile:
                    outfile.writelines(content_before_second_match)
                return True
            else:
                print('Second match not found in the file.')
                return False

        except FileNotFoundError:
            print(f'Error: Input file "{input_file}" not found.')
            return False
        except Exception as e:
            print(f'An error occurred: {str(e)}')
            return False

    def hasdisorder_atom(self, structure):

        ress = structure.get_residues()
        disorder_flag = False
        for res in ress:
            if res.is_disordered() == 1:
                disorder_flag = True
                return disorder_flag
        return disorder_flag

    def get_auth_comp_id_map(self, input_cif):
        """
            Extract the auth_comp_id mapping from an mmCIF dictionary.
        Parameters:
        mmcif_dict (dict): Parsed mmCIF dictionary

        Returns:
        dict: A dictionary mapping (chain_id, resseq) to auth_comp_id
        """

        parser = MMCIFParser()
        structure = parser.get_structure('structure', input_cif)
        mmcif_dict = parser._mmcif_dict
        chains = mmcif_dict['_atom_site.auth_asym_id']
        resseqs = mmcif_dict['_atom_site.label_seq_id']
        auth_comp_ids = mmcif_dict['_atom_site.auth_comp_id']

        auth_comp_id_map = {}
        for chain, resseq, auth_comp_id in zip(chains, resseqs, auth_comp_ids):
            try:
                resseq_key = int(resseq)
            except ValueError:
                resseq_key = resseq
            key = (chain, resseq_key)
            auth_comp_id_map[key] = auth_comp_id

        return auth_comp_id_map

    def get_formal_charge_map(self, input_cif):
        """
            Extract the pdbx_formal_charge mapping from an mmCIF dictionary.
        Parameters:
        mmcif_dict (dict): Parsed mmCIF dictionary

        Returns:
        dict: A dictionary mapping (chain_id, resseq) to pdbx_formal_charge
        """

        parser = MMCIFParser()
        structure = parser.get_structure('structure', input_cif)
        mmcif_dict = parser._mmcif_dict
        chains = mmcif_dict['_atom_site.auth_asym_id']
        resseqs = mmcif_dict['_atom_site.label_seq_id']
        formal_charges = mmcif_dict['_atom_site.pdbx_formal_charge']

        formal_charge_map = {}
        for chain, resseq, formal_charge in zip(chains, resseqs, formal_charges):
            try:
                resseq_key = int(resseq)
            except ValueError:
                resseq_key = resseq
            key = (chain, resseq_key)
            formal_charge_map[key] = formal_charge

        return formal_charge_map

    def save_updated_model(self, input_cif_file_one, input_cif_file):
        """
            Save the first model from the mmCIF file to a new mmCIF file with auth_comp_id.
        Parameters:
        input_cif_file (str): Input mmCIF file path
        output_cif_file (str): Output mmCIF file path
        """

        # Create the auth_comp_id_map
        auth_comp_id_map = self.get_auth_comp_id_map(input_cif_file_one)
        formal_charge_map = self.get_formal_charge_map(input_cif_file_one)

        # Extract the first model
        parser = MMCIFParser()
        structure = parser.get_structure('structure', input_cif_file)
        mmcif_dict = parser._mmcif_dict
        first_model = structure[0]

        # Prepare to add auth_comp_id
        if '_atom_site.auth_comp_id' not in mmcif_dict:
            mmcif_dict['_atom_site.auth_comp_id'] = []
        if '_atom_site.pdbx_formal_charge' not in mmcif_dict:
            mmcif_dict['_atom_site.pdbx_formal_charge'] = []

        # Get the existing residue information
        residues = mmcif_dict['_atom_site.label_comp_id']
        chains = mmcif_dict['_atom_site.auth_asym_id']
        resseqs = mmcif_dict['_atom_site.label_seq_id']

        # Add auth_comp_id based on the map
        for res, chain, resseq in zip(residues, chains, resseqs):
            try:
                resseq_key = int(resseq)
            except ValueError:
                resseq_key = resseq
            key = (chain, resseq_key)
            auth_comp_id = auth_comp_id_map.get(key, res)
            formal_charge = formal_charge_map.get(key, '?')
            mmcif_dict['_atom_site.auth_comp_id'].append(auth_comp_id)
            mmcif_dict['_atom_site.pdbx_formal_charge'].append(formal_charge)

        # Write the modified dictionary to a new mmCIF file
        io = MMCIFIO()
        io.set_dict(mmcif_dict)
        io.save(input_cif_file)

    def _structure_tomodel(self, pid, curmodelname):
        """
            Take structure object and output the used model object
        :param pid: String of anything or pdbid
        :param curmodelname: String of the model name
        :return: TEMPy model instance which will be used for the whole calculation
        """

        p = MMCIFParser()
        io = MMCIFIO()
        orgfilename = curmodelname
        match_text = 'data_'
        out_moderate_cif = curmodelname + '_moderated.cif'
        match = self.remove_lines_after_match(curmodelname, out_moderate_cif, match_text)
        if match:
            structure = p.get_structure(pid, out_moderate_cif)
            curmodelname = out_moderate_cif
        else:
            structure = p.get_structure(pid, curmodelname)

        if len(structure.get_list()) > 1:
            orgmodel = curmodelname + '_org.cif'
            os.rename(curmodelname, orgmodel)
            fstructure = structure[0]
            io.set_structure(fstructure)
            io.save(curmodelname)
            self.save_updated_model(orgmodel, curmodelname)
            usedframe = p.get_structure('first', curmodelname)
            print('!!!There are multiple models in the cif file. Here we only use the first for calculation.')
        else:
            usedframe = structure

        if self.hasdisorder_atom(usedframe):
            curmodelname = curmodelname + '_Alt_A.cif'
            io.set_structure(usedframe)
            print('There are alternative atom in the model here we only use A for calculations and saved as {}'
                  .format(curmodelname))
            io.save(curmodelname, select=NotDisordered())
            newstructure = p.get_structure(pid, curmodelname)
        else:
            newstructure = usedframe

        setattr(newstructure, "filename", orgfilename)
        tmodel = newstructure

        return tmodel

    def change_cifname(self):
        """
            If there is *_org.cif exist in the va folder, then change it back to the original file name
        """

        for file in os.listdir(self.dir):
            if file.endswith('_org.cif'):
                print('{} to {}'.format(file, file[:-8]))
                os.rename(self.dir + '/' + file, self.dir + '/' + file[:-8])

    # @profile
    def read_model(self):
        """
            Read models if '-f' argument is used
        """

        start = timeit.default_timer()
        if self.model is not None:
            modelname = self.model
            fullmodelname = []
            if self.emdid is None:
                for curmodel in modelname:
                    if not os.path.isfile(self.dir + curmodel) and os.path.isfile(curmodel):
                        fullmodelname.append(curmodel)
                    elif os.path.isfile(self.dir + curmodel):
                        fullmodelname.append(self.dir + curmodel)
                    else:
                        print('Something wrong with the input model name or path: {}.'.format(self.dir + curmodel))
            else:
                fullmodelname = [MAP_SERVER_PATH + self.subdir + '/va/' + curmodel for curmodel in modelname]

            try:
                modelsize = [os.stat(curmodelname).st_size for curmodelname in fullmodelname]
                pids = [os.path.basename(model)[:-4] for model in fullmodelname]
                inputmodel = []
                p = MMCIFParser()
                io = MMCIFIO()
                for pid, curmodelname in zip(pids, fullmodelname):
                    tmodel = self._structure_tomodel(pid, curmodelname)
                    inputmodel.append(tmodel)
                end = timeit.default_timer()
                print('Read model time: %s' % (end - start))
                print('------------------------------------')

                return inputmodel, pids, modelsize
            except:
                print('!!! File: %s does not exist or corrupted: %s!!!' % (fullmodelname, sys.exc_info()[1]))
                print('------------------------------------')
                inputmodel = None
                pid = None
                modelsize = None

                return inputmodel, pid, modelsize
        else:
            print('No model is given.')
            inputmodel = None
            pid = None
            modelsize = None

            return inputmodel, pid, modelsize

    def cifchains(self, fullmodelname):
        """
            For each model in fullmodelname, split each chain into a single mmcif file
        :param fullmodelname: a list of model file full names
        :return: a dirtornary which key as model and value as a list of chain cif file names
        """

        parser = MMCIFParser()
        chaindict = {}
        onechaindict = {}
        modelname = os.path.basename(fullmodelname)
        structure = parser.get_structure(modelname, fullmodelname)
        singlechainfiles = []
        io = MMCIFIO()
        for chain in structure.get_chains():
            io.set_structure(chain)
            name = '{}{}_chain_{}.cif'.format(self.dir, modelname, chain.id)
            print(name)
            singlechainfiles.append(name)
            io.save(name)
            onechaindict[chain.id] = name
        chaindict[fullmodelname] = onechaindict
        print(chaindict)
        print('Each chain cif files saved')

        return chaindict

    def updatechains(selfs, chaindict):
        """
            As Refmac need the symmetry in the chain to produce the model map, here we reload the model and each chain
            to a dictornary and save again to each chain so to produce the chain map
        :param chaindict:
        :return:
        """
        model = list(chaindict)[0]
        chains = list(chaindict[model].values())
        model_dict = MMCIF2Dict(model)
        io = MMCIFIO()
        for chain in chains:
            chain_dict = MMCIF2Dict(chain)
            if '_symmetry.space_group_name_H-M' in model_dict.keys():
                chain_dict['_symmetry.space_group_name_H-M'] = model_dict['_symmetry.space_group_name_H-M']
            else:
                chain_dict['_symmetry.space_group_name_H-M'] = 'P 1'
            io.set_dict(chain_dict)
            io.save(chain)

        return chaindict


    def chainmaps(self, chaindict):
        """
            Produce all the chain maps based on the chain model mmcifs
        :param chaindict: dictionary from function cifchains
        :return:
        """

        unit_cell, arr, origin = iotools.read_map(self.dir + self.mapname)
        dim = list(arr.shape)

        finaldict = {}
        errlist = []
        key = list(chaindict)[0]
        value = list(chaindict[key].values())
        chains = list(chaindict[key])
        modelmaps = []
        for chain, chainfile in zip(chains, value):
            print(chainfile)
            chainfilename = os.path.basename(chainfile)
            modelmapname = '{}{}_chainmap.map'.format(self.dir, chainfilename)
            try:
                modelmap = emda_methods.model2map(chainfile, dim, float(self.resolution),
                                                  unit_cell, maporigin=origin, outputpath=self.dir)
                emda_methods.write_mrc(modelmap, modelmapname, unit_cell, map_origin=origin)
                modelmaps.append(modelmapname)
            except:
                err = 'Simulating model({}) map error:{}.'.format(chainfilename, sys.exc_info()[1])
                errlist.append(err)
                sys.stderr.write(err + '\n')

            if errlist:
                try:
                    modelmap = emda_methods.model2map_gm(chainfile, float(self.resolution), dim,
                                                      unit_cell, maporigin=origin, outputpath=self.dir)
                    emda_methods.write_mrc(modelmap, modelmapname, unit_cell, map_origin=origin)
                    modelmaps.append(modelmapname)
                    print('Model is simulated by using GEMMI in Servalcat.')
                except:
                    err = 'Simulating model({}) map error:{}.'.format(chainfilename, sys.exc_info()[1])
                    errlist.append(err)
                    sys.stderr.write(err + '\n')
            finaldict[chain] = {chainfilename: os.path.basename(modelmapname)}

        return finaldict, errlist

    def modelstomaps(self):
        """
            Conver all models to corresponding maps and write it out
        :return:
        """

        if not self.model or not self.modelmap:
            print('If there is no model given or no modelmap in json or command line, '
                  'model map or model-map FSC will not be produced.')
        else:
            if self.method != 'tomo' and self.method != 'crys' and self.resolution:
                unit_cell, arr, origin = iotools.read_map(self.dir + self.mapname)
                dim = list(arr.shape)

                modelmaps = []
                errlist = []
                finaldict = {}
                realfinaldict = {}
                counter = 0
                # for each model produce a model map
                for model in self.model:
                    modelmapname = '{}{}_modelmap.map'.format(self.dir, model)
                    curmodelname = '{}{}'.format(self.dir, model)
                    try:
                        modelmap = emda_methods.model2map(self.dir + model, dim, float(self.resolution), unit_cell,
                                                          maporigin=origin, outputpath=self.dir)
                        emda_methods.write_mrc(modelmap, modelmapname, unit_cell, map_origin=origin)
                        modelmaps.append(modelmapname)
                    except:
                        err = 'Simulating model({}) map error:{}.'.format(model, sys.exc_info()[1])
                        errlist.append(err)
                        sys.stderr.write(err + '\n')

                    if errlist:
                        try:
                            modelmap = emda_methods.model2map_gm(self.dir + model, float(self.resolution), dim, unit_cell,
                                                                maporigin=origin, outputpath=self.dir)
                            emda_methods.write_mrc(modelmap, modelmapname, unit_cell, map_origin=origin)
                            modelmaps.append(modelmapname)
                            print('Model is simulated by using GEMMI in Servalcat.')
                        except:
                            err = 'Simulating model({}) map error:{}.'.format(model, sys.exc_info()[1])
                            errlist.append(err)
                            sys.stderr.write(err + '\n')
                    # Chain maps
                    chainerr = []
                    try:
                        tempdict = self.cifchains(curmodelname)
                        chaindict = self.updatechains(tempdict)
                    except:
                        err = 'Simulating chain map of model({}) error:{}.'.format(model, sys.exc_info()[1])
                        if chainerr:
                            errlist.extend(chainerr)
                            sys.stderr.write('Error in simulating chain map: ' + str(chainerr) + '\n')
                        errlist.append(err)
                        sys.stderr.write(err + '\n')
                    counter = counter + 1

                realfinaldict['modelmap'] = finaldict
                if errlist:
                    realfinaldict['modelmap']['err'] = {'mmap_err': errlist}

                try:
                    with codecs.open(self.dir + self.mapname + '_modelmaps.json', 'w',
                                     encoding='utf-8') as f:
                        json.dump(realfinaldict, f)
                except:
                    sys.stderr.write('Saving model/chain-map info to json error: {}.\n'.format(sys.exc_info()[1]))

                return modelmaps, errlist
            else:
                print("No model map is produced as this is either not a single particle entry or nothing specified "
                      "for method -m (please use: -m sp) or resolution not specified -s (please use: -s <value>).")

        return None, None

    # @profile
    def new_combinemap(self, odd_file, even_file, rawmapfullname):
        """
            Calculate rawmap from two half-maps and scale to primary map range.
            Apply primary map mean and std over the normalized raw map (mean=0, std=1)

        :param oddobj: odd map TEMPy instance
        :param evenobj: even map TEMPy instance
        :param rawmapfullname: string of raw map full name
        :return: raw map TEMPy instance
        """

        import gc

        with mrcfile.mmap(odd_file, mode='r+') as m:
            org_oddmap = m.data
            header = m.header
            if header.mode == 0 or header.mode == 1 or header.mode == 3 or header.mode == 6:
                oddmap = np.memmap.astype(org_oddmap, 'float32')
            else:
                oddmap = org_oddmap.copy()

        with mrcfile.mmap(even_file, mode='r+') as m:
            org_evenmap = m.data
            even_header = m.header
            if even_header.mode == 0 or even_header.mode == 1 or even_header.mode == 3 or even_header.mode == 6:
                evenmap = np.memmap.astype(org_evenmap, 'float32')
            else:
                evenmap = org_evenmap

        np.divide((oddmap - oddmap.mean()), oddmap.std(), out=oddmap)
        np.multiply(oddmap, evenmap.std(), out=oddmap)
        np.add(oddmap, (evenmap - evenmap.mean()), out=oddmap)
        np.divide(oddmap, evenmap.std(), out=oddmap)
        np.subtract(oddmap, oddmap.mean(), out=oddmap)
        np.divide(oddmap, oddmap.std(), out=oddmap)
        np.multiply(oddmap, self.primarymapstd, out=oddmap)
        np.add(oddmap, self.primarymapmean, out=oddmap)

        nstarts = [header.nxstart, header.nystart, header.nzstart]
        org_header = header
        self.write_map(rawmapfullname, oddmap, nstarts, org_header)
        rawmap = mrcfile.mmap(rawmapfullname, mode='r+')
        rawmap.fullname = rawmapfullname

        del evenmap
        del oddmap
        gc.collect()

        return rawmap


    # @profile
    def combinemap(self, oddobj, evenobj, rawmapfullname):
        """
            Calculate rawmap from two half-maps and scale to primary map range.
            Apply primary map mean and std over the normalized raw map (mean=0, std=1)

        :param oddobj: odd map TEMPy instance
        :param evenobj: even map TEMPy instance
        :param rawmapfullname: string of raw map full name
        :return: raw map TEMPy instance
        """

        oddmapdata = oddobj.data
        evenmapdata = evenobj.data
        normalised_odd = (oddmapdata - oddmapdata.mean()) / oddmapdata.std()
        normalised_even = (evenmapdata - evenmapdata.mean()) / evenmapdata.std()
        rawmapdata = normalised_odd + normalised_even
        normalised_raw = (rawmapdata - rawmapdata.mean()) / rawmapdata.std()
        scaled_normalised_raw = normalised_raw * self.primarymapstd + self.primarymapmean
        nstarts = [oddobj.header.nxstart, oddobj.header.nystart, oddobj.header.nzstart]
        org_header = oddobj.header
        self.write_map(rawmapfullname, scaled_normalised_raw, nstarts, org_header)
        rawmap = mrcfile.mmap(rawmapfullname, mode='r+')
        rawmap.fullname = rawmapfullname

    # @profile
    def read_halfmaps(self):
        """
            Read two half maps for FSC calculation
        :return:
        """

        halfeven = None
        halfodd = None
        rawmap = None
        twomapsize = 0.
        if self.emdid:
            mapone = MAP_SERVER_PATH + self.subdir + '/va/' + 'emd_' + self.emdid + '_half_map_1.map'
            maptwo = MAP_SERVER_PATH + self.subdir + '/va/' + 'emd_' + self.emdid + '_half_map_2.map'
            rawmapname = '{}{}/va/emd_{}_rawmap.map'.format(MAP_SERVER_PATH, self.subdir, self.emdid)
            if os.path.isfile(mapone) and os.path.isfile(maptwo):
                try:
                    halfodd = self.new_frommrc_totempy(mapone)
                    halfeven = self.new_frommrc_totempy(maptwo)
                    rawmap = self.new_combinemap(mapone, maptwo, rawmapname)
                    odd_mapsize = halfodd.header.nx * halfodd.header.ny * halfodd.header.nz
                    even_mapsize = halfeven.header.nx * halfeven.header.ny * halfeven.header.nz
                    twomapsize = odd_mapsize + even_mapsize
                    print('Raw map {} has been generated.'.format(rawmapname))
                except (IOError, ValueError) as e:
                    print('!!! Half-maps were given but something was wrong: {}'.format(e))
            else:
                halfeven = None
                halfodd = None
                rawmap = None
                twomapsize = 0.
                print('No half maps for this entry.')
        else:
            if self.evenmap is not None and self.oddmap is not None:
                mapone = self.dir + self.oddmap
                maptwo = self.dir + self.evenmap
                try:
                    rawmapname = '{}{}_{}_rawmap.map'.format(self.dir, self.oddmap, self.evenmap)
                    halfodd = self.new_frommrc_totempy(mapone)
                    halfeven = self.new_frommrc_totempy(maptwo)
                    rawmap = self.new_combinemap(mapone, maptwo, rawmapname)
                    odd_mapsize = halfodd.header.nx * halfodd.header.ny * halfodd.header.nz
                    even_mapsize = halfeven.header.nx * halfeven.header.ny * halfeven.header.nz
                    twomapsize = odd_mapsize + even_mapsize
                    print('Raw map {} has been generated.'.format(rawmapname))
                except (IOError, ValueError) as maperr:
                    print('!!! Half-maps were given but something was wrong: {}'.format(maperr))
            elif self.evenmap is None and self.oddmap is None:
                print('REMINDER: Both half maps are needed for FSC calculation!')
                halfeven = None
                halfodd = None
                rawmap = None
                twomapsize = 0.
            else:
                raise IOError('Another half map is needed for FSC calculation.')

        return halfeven, halfodd, rawmap, twomapsize

    def merge_json_objects(self, obj1, obj2):
        merged_obj = {}
        for key in set(obj1.keys()) | set(obj2.keys()):
            if key in obj1 and key in obj2 and isinstance(obj1[key], dict) and isinstance(obj2[key], dict):
                merged_obj[key] = self.merge_json_objects(obj1[key], obj2[key])
            elif key in obj1 and key in obj2:
                if isinstance(obj1[key], dict) and isinstance(obj2[key], dict):
                    merged_obj[key] = {**obj1[key], **obj2[key]}
                elif isinstance(obj1[key], dict) and not isinstance(obj2[key], dict):
                    merged_obj[key] = obj1[key]
                elif not isinstance(obj1[key], dict) and isinstance(obj2[key], dict):
                    merged_obj[key] = obj2[key]
                else:
                    merged_obj[key] = obj1[key]
            elif key in obj1:
                merged_obj[key] = obj1[key]
            elif key in obj2:
                merged_obj[key] = obj2[key]

        return merged_obj

    def merge_json_files(self, files):
        merged_data = {}

        for file in files:
            if os.path.getsize(file) > 0:
                with open(file, 'r') as f:
                    data = json.load(f)
                    merged_data = self.merge_json_objects(merged_data, data)
            else:
                sys.stderr.write('The {} is empty!\n'.format(file))

        return merged_data


    def merge_jsons(self):
        """
            Merge all generated json files to one file
        :return: None
        """

        jsonfiles = glob.glob(self.dir + '*.json')
        jsonfiles = [jfile for jfile in jsonfiles if 'all.json' not in jfile]
        fuldata = {}

        filename = os.path.basename(self.mapname) if self.emdid is None else self.emdid
        fuldata = self.merge_json_files(jsonfiles)


        finaldata = dict()
        if self.emdid is not None:
            finaldata[self.emdid] = fuldata
            output = '{}emd_{}_all.json'.format(self.dir, self.emdid)
        else:
            finaldata[filename] = fuldata
            output = '{}{}_all.json'.format(self.dir, filename)
        with open(output, 'w') as out:
            json.dump(finaldata, out)

        checks_json_files = glob.glob(f'{self.dir}/va_feature_extraction/*.json')
        checks_json_files = [cfile for cfile in checks_json_files if '_va_feature_extraction.json' not in cfile]
        checks_output_file = f'{self.dir}/va_feature_extraction/{filename}_va_feature_extraction.json'
        checks_data = self.merge_json_files(checks_json_files)
        checks_full_data = {str(self.emdid): checks_data}
        out_json(checks_full_data, checks_output_file)

        # Get the assessment output
        assess_out_dir = f'{self.dir}/va_feature_assessment'
        feature_assessment(checks_output_file, assess_out_dir)

        return None

    def merge_bars(self):
        """
            Merge all bars to one png file
        :return: None
        """

        try:
            barfiles = glob.glob(self.dir + '*_bar.png')
            barfiles = [jfile for jfile in barfiles if 'allbars.png' not in jfile]

            images = [Image.open(img_path) for img_path in barfiles]
            total_width = images[0].width
            total_height = sum(img.height for img in images)

            new_image = Image.new("RGB", (total_width, total_height))

            y_offset = 0
            for img in images:
                new_image.paste(img, (0, y_offset))
                y_offset += img.height

            output_path = '{}/{}_allbars.png'.format(self.dir, os.path.basename(self.mapname))
            new_image.save(output_path)
        except Exception as e:
            print('No bar to to merged')
            print('The error is {}'.format(e))

        return None


    def write_recl(self):
        """
            Write recl into a json file
        :return: None
        """

        if self.contourlevel is not None:
            dictrecl = dict()
            dictrecl['recl'] = self.contourlevel
            lastdict = dict()
            lastdict['recommended_contour_level'] = dictrecl
            filename = self.mapname
            output = '{}{}_recl.json'.format(self.dir, os.path.basename(filename))
            with open(output, 'w') as out:
                json.dump(lastdict, out)

        return None

    def write_version(self):
        """
            Write version
        :return: None
        """

        versiondict = dict()
        versiondict['version'] = __version__
        filename = self.mapname
        output = '{}{}_version.json'.format(self.dir, os.path.basename(filename))
        with open(output, 'w') as out:
            json.dump(versiondict, out)

        return None


    def finiliszejsons(self):
        """
            Function to write out contour level json, version information and combine all jsons to one
        :return: None
        """

        start = timeit.default_timer()
        self.write_recl()
        self.write_version()
        self.merge_bars()
        self.merge_jsons()
        stop = timeit.default_timer()
        print('Merge JSONs: %s' % (stop - start))
        print('------------------------------------')

        return None

    #@staticmethod
    def memmsg(self, mapsize):
        """
            Memory usage reminder based on memory prediction
        :return:
        """
        # When there is no emdid given, we use one level above the given "dir" to save the memory prediction file
        # input.csv. If emdid is given, we use the. self.dir is like /abc/cde/ so it needs to used os.path.dirname()
        # twice.

        if self.emdid:
            vout = MAP_SERVER_PATH
        else:
            vout = os.path.dirname(os.path.dirname(self.dir)) + '/'
        if os.path.isfile(vout + 'input.csv') and os.path.getsize(vout + 'input.csv') > 0:
            mempred = ValidationAnalysis.mempred(vout + 'input.csv', 2 * mapsize)
            if mempred == 0 or mempred is None:
                print('No memory prediction.')
                return None
            else:
                print('The memory you may need is %s M' % mempred)
                assert mempred < psutil.virtual_memory().total / 1024 / 1024, \
                    'The memory needed to run may exceed the total memory you have on the machine.'
                return mempred
        else:
            print('No memory data available for prediction yet')
            return None



