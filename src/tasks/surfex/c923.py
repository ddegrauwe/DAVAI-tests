# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, unicode_literals, division

from footprints import FPDict

import vortex
from vortex import toolbox
from vortex.layout.nodes import Task, Family, Driver
from common.util.hooks import update_namelist
import davai

from davai_taskutil.mixins import DavaiIALTaskMixin, IncludesTaskMixin


class C923(Task, DavaiIALTaskMixin, IncludesTaskMixin):

    experts = [FPDict({'kind':'fields_in_file'})]
    _taskinfo_kind = 'statictaskinfo'

    def _flow_input_name_block(self):
        return '-'.join([self.conf.prefix,
                         'make-domain',
                         self.conf.model,
                         self.conf.geometry.tag])

    def _flow_input_pgd_block(self):
        return '-'.join([self.conf.prefix,
                         'pgd',
                         self.conf.model,
                         self.conf.geometry.tag])
                         
    def output_block(self):
        return '-'.join([self.conf.prefix,
                         self.tag])

    def process(self):
        self._wrapped_init()
        self._notify_start_inputs()

        # 0./ Promises
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            self._wrapped_promise(**self._promised_expertise())
            #-------------------------------------------------------------------------------

        # 1.1.0/ Reference resources, to be compared to:
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            pass
            
            #-------------------------------------------------------------------------------

        # 1.1.1/ Static Resources:
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            self._load_usual_tools()  # LFI tools, ecCodes defs, ...
            #-------------------------------------------------------------------------------
            
            self._wrapped_input(
                role           = 'WaterPercentageDB',
                format         = 'bin',
                genv           = self.conf.appenv_clim,
                geometry       = 'global2m5',
                kind           = 'water_percentage',
                local          = 'Water_Percentage',
                source         = 'GTOPO30',
            )

            self._wrapped_input(
                role           = 'OrographyDerivedParameters',
                format         = 'bin',
                genv           = self.conf.appenv_clim,
                geometry       = 'global2m5',
                kind           = 'misc_orography',
                local          = 'misc_orography.tgz',
                source         = 'GTOPO30',
            )

            self._wrapped_input(
                role           = 'UrbanisationDB',
                format         = 'bin',
                genv           = self.conf.appenv_clim,
                geometry       = 'global2m5',
                kind           = 'urbanisation',
                local          = 'Urbanisation',
                source         = 'GTOPO30',
            )

        # 1.1.2/ Static Resources (namelist(s) & config):
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            # daand: moved it to 2.1/ because it's generated by make_lam_domain
            pass
            #-------------------------------------------------------------------------------

        # 1.1.3/ Static Resources (executables):
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            #-------------------------------------------------------------------------------
            tbx = self.flow_executable()
            #-------------------------------------------------------------------------------

        # 1.2/ Flow Resources (initial): theoretically flow-resources, but statically stored in input_shelf
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            pass
            #-------------------------------------------------------------------------------

        # 2.1/ Flow Resources: produced by another task of the same job
        if 'fetch' in self.steps:

            #-------------------------------------------------------------------------------

            tbtrunc=self._wrapped_input(
                role           = 'TruncationDefinition',
                block          = self._flow_input_name_block(),
                experiment     = self.conf.xpid,
                format         = 'ascii',
                geometry       = self.conf.geometry.tag,
                kind           = 'geoblocks',
                local          = 'truncation_blocks.nam',
                target         = 'c923_orography',
            )

            #-------------------------------------------------------------------------------

            tbgeo=self._wrapped_input(
                role           = 'GeometryDefinition',
                block          =  self._flow_input_name_block(),
                experiment = self.conf.xpid,
                format         = 'ascii',
                geometry = self.conf.geometry.tag,
                kind           = 'geoblocks',
                local          = 'geometry_blocks.nam',
                target         = 'c923',
            )

            #-------------------------------------------------------------------------------
            
            self._wrapped_input(
                role           = 'Namelist',
                binary         = 'arpege',
                format         = 'ascii',
                genv           = self.conf.appenv_clim,
                hook_geo       = (update_namelist, tbgeo, tbtrunc),
                intent         = 'inout',
                kind           = 'namelist',
                local          = 'fort.4',
                source         = self.conf.model+'/namel_c923_orography',
            )

            #-------------------------------------------------------------------------------

            # PGD file
            self._wrapped_input(
                role           = 'Pgd',
                block          = self._flow_input_pgd_block(),
                experiment     = self.conf.xpid,
                format         = 'fa',
                kind           = 'pgd',
                local          = 'Neworog',
                nativefmt      = 'fa',
            )
            #-------------------------------------------------------------------------------

        # 2.2/ Compute step
        if 'compute' in self.steps:
            self._notify_start_compute()
            self.sh.title('Toolbox algo = tbalgo')
            tbalgo = toolbox.algo(
                conf           = '923',
                engine         = 'parallel',
                kind           = 'c923',
                orog_in_pgd    = True,
                step           = '1',
            )
            print(self.ticket.prompt, 'tbalgo =', tbalgo)
            print()
            self.component_runner(tbalgo, tbx)
            #-------------------------------------------------------------------------------
            #self.run_expertise()
            #-------------------------------------------------------------------------------

        # 2.3/ Flow Resources: produced by this task and possibly used by a subsequent flow-dependant task
        if 'backup' in self.steps:
            #-------------------------------------------------------------------------------
            self._wrapper_output = toolbox.output(
                role           = 'ClimFile',
                block          = self.output_block(),
                experiment     = self.conf.xpid,
                format         = 'fa',
                kind           = 'clim_model',
                local          = 'Const.Clim',
            )

            #-------------------------------------------------------------------------------

        # 3.0.1/ Davai expertise:
        if 'late-backup' in self.steps or 'backup' in self.steps:
            pass
            #self._wrapped_output(**self._output_expertise())
            #self._wrapped_output(**self._output_comparison_expertise())
            #-------------------------------------------------------------------------------

        # 3.0.2/ Other output resources of possible interest:
        if 'late-backup' in self.steps or 'backup' in self.steps:
            self._wrapped_output(**self._output_listing())
            #-------------------------------------------------------------------------------

