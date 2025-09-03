from pydantic import BaseModel, Field
from typing import Optional


class DataSettings(BaseModel):
    """
        Dataclass of settings for STEAM analyses
        This will be populated either form a local settings file (if flag_permanent_settings=False)
        or from the keys in the input analysis file (if flag_permanent_settings=True)
    """
    comsolexe_path: Optional[str] = Field(default=None,
                                          title="Comsol executable path",
                                          description="Absolute path to comsol.exe, only version 5.3a or 6.0 are supported",
                                          examples=[r"C:\Program Files\COMSOL\COMSOL53a\Multiphysics\bin\win64\comsol.exe"])
    JAVA_jdk_path: Optional[str] = Field(default=None,
                                         title="Java jdk executable path",
                                         description="Absolute path to Java jdk folder, only version jdk1.8.0_281 is supported.",
                                         examples=[r"C:\Program Files\Java\jdk1.8.0_281"])
    CFunLibPath: Optional[str] = Field(default=None,
                                       title="CFun dlls path",
                                       description="Absolute path to folder containing dll files with material properties compiled from C functions (CFUN)",
                                       examples=[r"C:\STEAM\MaterialsLibrary\V0.1"])
    ANSYS_path: Optional[str] = Field(default=None,
                                      title="ANSYS executable path",
                                      description="Absolute path to ANSYSvvv.exe. Only version 19.2 has been tested to work correctly.",
                                      examples=[r"C:\Program Files\ANSYS Inc\v192\ansys\bin\winx64\ANSYS192.exe"])
    COSIM_path: Optional[str] = Field(default=None,
                                      title="COSIM executable path",
                                      description="Absolute path to COSIM.exe. Only version 0.5 is supported.",
                                      examples=[r"C:\STEAM\steam-cosim_v0.5.exe"])
    Dakota_path: Optional[str] = Field(default=None,
                                       title="DAKOTA executable path",
                                       description="Full path to dakota.exe. Only version 6.16.0 has been tested to work correctly.",
                                       examples=[r"C:\Program Files\dakota-6.16.0-public-windows.Windows.x64-cli\bin\dakota.exe"])
    ffmpeg_path: Optional[str] = Field(default=None,
                                       title="ffmpeg executable path",
                                       description="Absolute path to ffmpeg.exe.",
                                       examples=[r"C:\Program Files\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"])
    FiQuS_path: Optional[str] = Field(default=None,
                                      title="FiQuS folder path",
                                      description="Absolute path to FiQuS folder containing its source code",
                                      examples=[r"C:\STEAM\steam-fiqus", r"C:\STEAM\steam-fiqus-dev"])
    GetDP_path: Optional[str] = Field(default=None,
                                      title="GetDP executable path",
                                      description="Absolute path to getdp.exe. Either official GetDP and CERNGetDP can be used, depending on the model requirements",
                                      examples=[r"C:\STEAM\cerngetdp_2024.1.0\getdp_2024.1.0.exe", r"C:\getdp-3.5.0-Windows64\getdp.exe"])
    LEDET_path: Optional[str] = Field(default=None,
                                      title="LEDET executable path",
                                      description="Absolute path to LEDET.exe. This version of SKD is compatible with version XXX or above",  # TODO update version
                                      examples=[r"C:\STEAM\LEDET_v2_02_11.exe"])
    ProteCCT_path: Optional[str] = Field(default=None,
                                         title="ProteCCT executable path",
                                         description="Absolute path to ProteCCT.exe.",
                                         examples=[r"C:\STEAM\ProteCCT.exe"])
    PSPICE_path: Optional[str] = Field(default=None,
                                       title="PSPICE executable path",
                                       description="Absolute path to psp_cmd.exe. Version 17.4 has been tested to work correctly.",
                                       examples=[r"C:\Cadence\SPB_17.4\tools\bin\psp_cmd.exe"])
    PyBBQ_path: Optional[str] = Field(default=None,
                                      title="pyBBQ python script path",
                                      description="Absolute path to pyBBQ.py",
                                      examples=[r"C:\STEAM\pyBBQ.py"])
    XYCE_path: Optional[str] = Field(default=None,
                                     title="XYCE executable path",
                                     description="Absolute path to Xyce.exe. Version 7.5 has been tested to work correctly.",
                                     examples=[r"C:\Program Files\Xyce 7.5 NORAD\bin\Xyce.exe"])
    PSPICE_library_path: Optional[str] = Field(default=None,
                                               title="PSPICE components library path",
                                               description="Absolute path to a folder containing STEAM PSPICE library",
                                               examples=[r"C:\gitlab\steam-pspice-library"])
    MTF_credentials_path: Optional[str] = Field(default=None,
                                                title="MTF credentials file path",
                                                description="Absolute path to the txt file containing the credentials for MTF login. CERN internal use only.",
                                                examples=[r"C:\steam-supplements\file.txt"])
    local_library_path: Optional[str] = Field(default=None,
                                              title="STEAM models library path",
                                              description="Absolute or relative path to STEAM models library folder. If relative, it is relative to folder with analysis.yaml file",
                                              examples=[r"../builders/model_library", r"C:\STEAM\model_library"])
    local_ANSYS_folder: Optional[str] = Field(default=None,
                                              title="ANSYS local folder path",
                                              description="Absolute or relative path to ANSYS folder for writing results (output) folders and files"
                                                          "RELATIVE PATH IS TO THE PARENT FOLDER OF CALLING SCRIPT. RELATIVE PATH SHOULD ONLY BE USED FOR TESTS!",
                                              examples=[r"output/output_library/ANSYS", r"C:\tempANSYS"])
    local_COSIM_folder: Optional[str] = Field(default=None,
                                              title="COSIM local folder path",
                                              description="Absolute or relative path to COSIM folder for writing results (output) folders and files"
                                                          "RELATIVE PATH IS TO THE PARENT FOLDER OF CALLING SCRIPT. RELATIVE PATH SHOULD ONLY BE USED FOR TESTS!",
                                              examples=[r"output/output_library/COSIM", r"C:\tempCOSIM"])
    local_Dakota_folder: Optional[str] = Field(default=None,
                                               title="Dakota local folder path",
                                               description="Absolute or relative path to Dakota folder for writing results (output) folders and files"
                                                           "RELATIVE PATH IS TO THE PARENT FOLDER OF CALLING SCRIPT. RELATIVE PATH SHOULD ONLY BE USED FOR TESTS!",
                                               examples=[r"output/output_library/Dakota", r"C:\tempDakota"])
    local_FiQuS_folder: Optional[str] = Field(default=None,
                                              title="FiQuS local folder path",
                                              description="Absolute or relative path to FiQuS folder for writing results (output) folders and files"
                                                          "RELATIVE PATH IS TO THE PARENT FOLDER OF CALLING SCRIPT. RELATIVE PATH SHOULD ONLY BE USED FOR TESTS!",
                                              examples=[r"output/output_library/FiQuS", r"C:\tempFiQuS"])
    local_LEDET_folder: Optional[str] = Field(default=None,
                                              title="LEDET local folder path",
                                              description="Absolute or relative path to LEDET folder for writing results (output) folders and files"
                                                          "RELATIVE PATH IS TO THE PARENT FOLDER OF CALLING SCRIPT. RELATIVE PATH SHOULD ONLY BE USED FOR TESTS!",
                                              examples=[r"output/output_library/LEDET", r"C:\tempLEDET"])
    local_ProteCCT_folder: Optional[str] = Field(default=None,
                                                 title="ProteCCT local folder path",
                                                 description="Absolute or relative path to ProteCCT folder for writing results (output) folders and files"
                                                             "RELATIVE PATH IS TO THE PARENT FOLDER OF CALLING SCRIPT. RELATIVE PATH SHOULD ONLY BE USED FOR TESTS!",
                                                 examples=[r"output/output_library/ProteCCT", r"C:\tempProteCCT"])
    local_PSPICE_folder: Optional[str] = Field(default=None,
                                               title="PSPICE local folder path",
                                               description="Absolute or relative path to PSPICE folder for writing results (output) folders and files"
                                                           "RELATIVE PATH IS TO THE PARENT FOLDER OF CALLING SCRIPT. RELATIVE PATH SHOULD ONLY BE USED FOR TESTS!",
                                               examples=[r"output/output_library/PSPICE", r"C:\tempPSPICE"])
    local_PyBBQ_folder: Optional[str] = Field(default=None,
                                              title="PyBBQ local folder path",
                                              description="Absolute or relative path to PyBBQ folder for writing results (output) folders and files"
                                                          "RELATIVE PATH IS TO THE PARENT FOLDER OF CALLING SCRIPT. RELATIVE PATH SHOULD ONLY BE USED FOR TESTS!",
                                              examples=[r"output/output_library/PyBBQ", r"C:\tempPyBBQ"])
    local_PyCoSim_folder: Optional[str] = Field(default=None,
                                                title="PyCoSim local folder path",
                                                description="Absolute or relative path to PyCoSim folder for writing results (output) folders and files"
                                                            "RELATIVE PATH IS TO THE PARENT FOLDER OF CALLING SCRIPT. RELATIVE PATH SHOULD ONLY BE USED FOR TESTS!",
                                                examples=[r"output/output_library/PyCoSim", r"C:\tempPyCoSim"])
    local_SIGMA_folder: Optional[str] = Field(default=None,
                                              title="SIGMA local folder path",
                                              description="Absolute or relative path to SIGMA folder for writing results (output) folders and files"
                                                          "RELATIVE PATH IS TO THE PARENT FOLDER OF CALLING SCRIPT. RELATIVE PATH SHOULD ONLY BE USED FOR TESTS!",
                                              examples=[r"output/output_library/SIGMA", r"C:\tempSIGMA"])
    local_XYCE_folder: Optional[str] = Field(default=None,
                                             title="XYCE local folder path",
                                             description="Absolute or relative path to XYCE folder for writing results (output) folders and files"
                                                         "RELATIVE PATH IS TO THE PARENT FOLDER OF CALLING SCRIPT. RELATIVE PATH SHOULD ONLY BE USED FOR TESTS!",
                                             examples=[r"output/output_library/XYCE", r"C:\tempXYCE"])
