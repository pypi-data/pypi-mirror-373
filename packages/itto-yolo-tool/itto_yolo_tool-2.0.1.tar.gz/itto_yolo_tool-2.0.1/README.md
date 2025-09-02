# Yolo-integrated-training-tool:Ver-2.0.1  
  
## Introduction
This is a Yolo integrated training tool, because when I usually use YOLO for training, I often encounter problems such as labeling, file conversion, setting configuration files, setting sample allocation ratios, and verifying various training tasks and results. Due to the scattered nature of each tool, I wanted to write an ensemble tool to facilitate the quick construction of the YOLO training workspace

![main_menu.jpg is initialing](./README_images/en/main_menu.jpg)
  
## Quick Start

### Environment

python=3.9~3.11  
pytorch  
ultralytics  
PyQt5  

### Installation

Method 1: Install using pip
Use command:
```cmd
pip install itto-yolo-tool
```
Launch the application:
```cmd
itto
```

Method 2: Use Git cloning
Windows/Linux/Mac: Enter the following command:
```cmd
git clone  https://github.com/RinST-Dreaming/Yolo-integrated-training-tool.git
```  
Alternatively, you can directly download the source code. zip file from the main page

Run the following command in the directory:
```cmd
python setup.py install
``` 

Launch the application:
```cmd
itto
```

### Usage method
Before use, please ensure that you have configured the YOLO training environment!!!

Startup:   
Simply open the source code folder and run the main.exe file to see the software interface
  
Training steps:  

1. Create a folder locally, which is the working directory for training your YOLO model  
   ![图片正在加载中](./README_images/en/work_space_dir.jpg)

2. Click the "Browse" button on the right side of the workspace to find the folder you created  
   ![图片正在加载中](./README_images/en/browse_button.jpg)
   
3. Click the "Create subfolders in workspace" button to create folders with different functions  
   ![图片正在加载中](./README_images/en/create_work_frame_button.jpg)
   - Files_waiting_for_classify: Store all your dataset images and annotation files, and wait for them to be randomly assigned to three other folders  
   - Train: Store the training dataset for YOLO  
   - Val: Store YOLO's validation dataset  
   - Test: Store the dataset for manual validation after training the YOLO model  

4. Copy all the datasets you are preparing to train into the "files_waiting_for_classify" folder and classify them into folders inside the "files_waiting_for_classify" folder according to the following rules:  
   - Images: Store image data
   - Labels: storing txt files for annotations
   - Labels-xml: storing annotated XML files  
    ![图片正在加载中](./README_images/en/sub_dir_branch.jpg)
  
5. If your image has not been annotated with data yet, click the "rolabelimg" button to start the "rolabelimg" annotation tool and annotate the dataset. The official website and tutorial are as follows: [rolabelimg](https://github.com/cgvict/roLabelImg)  
   ![图片正在加载中](./README_images/en/rolabelimg_button.jpg)

6. Find the "Add Annotation Name" window on the right and enter the model name you annotated, one on each line  
   ![图片正在加载中](./README_images/en/browse_button.jpg)

7. Click the "Create dataset. yaml" button to create a configuration file  
   ![图片正在加载中](./README_images/en/create_A.yaml_button.jpg)

8. Click the "Randomly Classify Images" button to allocate the "files_waiting_for_classify" folder to the other three categories according to a certain proportion (the allocation ratio can be configured in the right window)  
   ![图片正在加载中](./README_images/en/randomly_categorize_button.jpg)
      
9.  Click the "XML_to-txt" button to convert the XML file annotated with Rolabelimg into a TXT file that YOLO can recognize  
    ![图片正在加载中](./README_images/en/convert_xml_to_txt_button.jpg)

10. (Optional) Click on the "XML_Cvert_amine" button, manually check if the annotation conversion is correct, press any key to switch to the next one, and press the "q" key to exit  
    ![图片正在加载中](./README_images/en/convert_examination_button.jpg)

11. Configure YOLO training commands. If you are new to YOLO model training, it is recommended to click on "YOLO Training Basic Settings", where you can find some pre-set training parameters; If you want to customize training commands, you can click on "YOLO Training Command Advanced Settings". If the internal content of this setting is left blank, it will default to "Training Basic Settings"  
    ![图片正在加载中](./README_images/en/basic_training_setting_button.jpg)
    ![图片正在加载中](./README_images/en/command_training_setting_button.jpg)

12. Click the "Start YOLO Training" button and wait for the training to complete  
    ![图片正在加载中](./README_images/en/start_yolo_training_button.jpg)

------Waiting for the training to end, congratulations on successfully completing a YOLO model training------

13.  (Optional) Copy the "best. pt" file obtained from training to your working directory, click the "Start YOLO Training Results Verification" button, and manually verify the training effect of the model   
    ![图片正在加载中](./README_images/en/start_yolo_validation_button.jpg)

# Acknowledgements and Copyright Statement
This project uses [rolabelimg](https://github.com/cgvict/roLabelImg). The tool is developed by [cgvit and wkkmike] and follows the [MIT License] license.   
Due to the lack of updates for the Rolabelimg project for a long time, we have created a fork of this project [Rolabelimg-fix](https://github.com/RinST-Dreaming/roLabelImg-fix) to continue to maintain and update it, and apply it to the project in practice. Thank you again to the open source workers of Rolabelimg.  
Thanks [rolabelimg_commits](https://github.com/cgvict/roLabelImg/pull/37) Provides better error resolution ideas for Rolabelimg regarding floating-point issues