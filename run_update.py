__author__ = 'zwhitman'
__name__ = 'run_update'

# if __name__ == "__main__":
#
# start
#

import os
import update_tools as ut
import sys
import traceback
import shutil

# base path
base_path = str(os.path.dirname(os.path.realpath('__file__'))).replace("\\", "/")
base_path = base_path+'/new_ago/update_tools'

# read agoTools-config.ini file for configuration settings
cfg = ut.ConfigFile(base_path)
# dm.lgr2.info('Config file has been read.')

# sets up directories and logging function
dm = ut.DirMGMT()
dm.dirMgmt()

# Create list of MXDs from the MXD folder
file_list = []
for root, dirs, files in os.walk(r''+cfg.mxd_folder):
    for f in files:
        file_list.append(f)

# Run update on each MXD in the file_list variable
for mxd in file_list:
    try:

        # call layer properties
        glp = ut.GetLayerProperties(cfg.mxd_folder, mxd)
        dm.lgr2.info(glp.utag)

        # Create log folder structure
        dm.createSetLogFile(glp.lyr_name)
        dm.lgr2.info(glp.lyr_name)
        dm.lgr2.info('Log folder created.')


        # Create settings file
        settings_file = str(base_path+"/settings/settings_"+mxd[:-4]+".ini")
        ut.SettingsFile(base_path, mxd).createSetFile(glp.lyr_name,
                                                       cfg.mxd_folder,
                                                       glp.generate_tags(),
                                                       glp.lyr_desc,
                                                       cfg.ago_group,
                                                       cfg.user_profile,
                                                       cfg.pswd)
        dm.lgr2.info('Settings File created. Path: '+settings_file)

        # update the feature service
        ut.complete_update(base_path, cfg.mxd_folder, mxd, settings_file)
        dm.lgr2.info('The complete_update function ran successfully.')
        sf = ut.ReadSF(settings_file)
        ut.AGOLHandler(cfg.user_profile,
                                  cfg.pswd,
                                  sf.servicename,
                                  glp.utag).update_attributes(settings_file)
        dm.lgr2.info('The update_attributes function ran successfully.')

        # Clean up files
        log_settings = os.path.join(dm.logDir, sf.servicename, 'settings')
        log_sd = os.path.join(dm.logDir, sf.servicename, 'sd')
        shutil.copytree(base_path+'/tempDir', log_sd)
        shutil.copytree(base_path+'/settings', log_settings)
        shutil.rmtree(os.path.join(base_path, 'settings'))
        shutil.rmtree(os.path.join(base_path, 'tempDir'))
        os.mkdir(os.path.join(base_path, 'settings'))
        os.mkdir(os.path.join(base_path, 'tempDir'))

        # Clean up files
        # log_settings = os.path.join(dm.logDir, sf.servicename, 'settings', sf.servicename + ".ini")
        # log_sd = os.path.join(dm.logDir, sf.servicename, 'sd', sf.servicename + ".sd")
        # try:
        #     finalSD = os.path.join(base_path, 'tempDir', sf.servicename.replace('_', ' ') + ".sd")
        #     os.rename(finalSD, log_sd)
        # except:
        #     finalSD = os.path.join(base_path, 'tempDir', sf.servicename.replace('', '_') + ".sd")
        #     os.rename(finalSD, log_sd)
        #
        # os.rename(settings_file, log_settings)
        dm.lgr2.info('\n'+mxd[:-4] + ' has run successfully. SD and settings files have been moved to log folder.')
    except:
        dm.lgr2.error('Got an exception on main handler')
        e = sys.exc_info()[0]
        dm.lgr2.error('Error: %s' % str(e))
        dm.lgr2.error(traceback.format_exc())
        try:
            settings_file = str(base_path+"/settings/settings_"+mxd[:-4]+".ini")
            sf = ut.ReadSF(settings_file)

            # Clean up files
            log_settings = os.path.join(dm.logDir, sf.servicename, 'settings')
            log_sd = os.path.join(dm.logDir, sf.servicename, 'sd')
            shutil.copytree(base_path+'/tempDir', log_sd)
            shutil.copytree(base_path+'/settings', log_settings)
            shutil.rmtree(os.path.join(base_path, 'settings'))
            shutil.rmtree(os.path.join(base_path, 'tempDir'))
            os.mkdir(os.path.join(base_path, 'settings'))
            os.mkdir(os.path.join(base_path, 'tempDir'))

            # settings_file = os.path.join(base_path, 'settings', 'settings_'+mxd[:-4])
            # sf = ut.ReadSF(settings_file)
            # log_settings = os.path.join(dm.logDir, sf.servicename, 'settings', sf.servicename + ".ini")
            # log_sd = os.path.join(dm.logDir, sf.servicename, 'sd', sf.servicename + ".sd")
            # finalSD = os.path.join(base_path, 'tempDir', sf.servicename.replace('_', ' ') + ".sd")
            # os.rename(settings_file, log_settings)
            # os.rename(finalSD, log_sd)
            # dm.lgr2.error(mxd[:-4] + ' has not run successfully. SD and settings files have been moved to log folder.')
        except:
            dm.lgr2.error("Couldn't clean up folders because SD and settings files were not found. Deleting temp folders now.")
            e = sys.exc_info()[0]
            dm.lgr2.error('Error: %s' % str(e))
            dm.lgr2.error(traceback.format_exc())
            shutil.rmtree(os.path.join(base_path, 'settings'))
            shutil.rmtree(os.path.join(base_path, 'tempDir'))
            os.mkdir(os.path.join(base_path, 'settings'))
            os.mkdir(os.path.join(base_path, 'tempDir'))
        pass


