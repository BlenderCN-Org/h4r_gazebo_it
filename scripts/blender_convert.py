import bpy,bmesh
import os
import zipfile
import os, shutil
import re
import io
from copy import copy
from math import sqrt
from math import atan2
from math import pi
from mathutils import Matrix

import math
import mathutils

def getBoundingBoxesForObjects():
#     selected = bpy.context.selected_objects
#     
#     for obj in selected:

# #         
# #         
# #         
# #         
# #         
# #         
# #         #cursor to old object center
# #         bpy.context.scene.cursor_location = cur_loc
# #         
# #         #restore original object center
# #         bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
# 
# 
#         #ensure origin is centered on bounding box center
#         bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
#         #create a cube for the bounding box
#         bpy.ops.mesh.primitive_cube_add() 
#         #our new cube is now the active object, so we can keep track of it in a variable:
#         bound_box = bpy.context.active_object 
#      
#         #copy transforms
#         bound_box.dimensions = obj.dimensions
#         bound_box.location = obj.location
#         bound_box.rotation_euler = obj.rotation_euler
         
    pass


def rotateObjAroundCenter(obj,rot): 
    
    for i, angle in enumerate("XYZ"):
    
        rot_mat = Matrix.Rotation(rot[i], 4, angle)
        
        orig_loc, orig_rot, orig_scale = obj.matrix_world.decompose()
        orig_loc_mat = Matrix.Translation(orig_loc)
        orig_rot_mat = orig_rot.to_matrix().to_4x4()
        orig_scale_mat = Matrix.Scale(orig_scale[0],4,(1,0,0)) * Matrix.Scale(orig_scale[1],4,(0,1,0)) * Matrix.Scale(orig_scale[2],4,(0,0,1))
        
        obj.matrix_world = orig_loc_mat * rot_mat * orig_rot_mat * orig_scale_mat 
    
    pass

def createDir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir
    
    


def getCurrentSceneMinMaxCoords():
    #Current scene

    max=None
    min=None
    
    scene = bpy.context.scene
    for obj in scene.objects:
        if obj.mode == 'EDIT':
            bm = bmesh.from_edit_mesh(obj.data)
            vertices = bm.verts
        
        else:
            vertices = obj.data.vertices

        verts = [obj.matrix_world * vert.co for vert in vertices]
        for v in verts:
            if(min==None):
                min=copy(v)
                max=copy(v)
            
            #print(v)
            
            for c in range(3):
                if(min[c]>v[c]):
                    min[c]=v[c]
                    #print("min"+str(c)+"="+str(v[c]))
                    
                    
                if(max[c]<v[c]):
                    max[c]=v[c]
                    #print("max"+str(c)+"="+str(v[c]))
                
    return [min,max]


def getScales(target_sizes):
    minmax=getCurrentSceneMinMaxCoords()
    scales=[1.0,1.0,1.0]
    sizes=[0,0,0]
    
    print("Target Sizes of Model are:")
    print(target_sizes)
    
    
    for s in range(3):
        sizes[s]=minmax[1][s]-minmax[0][s]
            
    
    
    
    print("Found the following sizes")
    print(sizes)
    
    
    
    
    for s in range(3):
        if(target_sizes[s]!=None):
            if(abs(sizes[s] - target_sizes[s]) >0.001):
                scales[s]=target_sizes[s]/sizes[s]
                
                
    print("resulting in following scales")
    print(scales)
    return scales

def analyze_obj(obj_path, out_path, dimensions=None, rot=None):
    file_name, file_extension = os.path.splitext(os.path.basename(obj_path))
    scene = bpy.context.scene
    
    
    
    
    
    
    
    ret_data={}
 
    # Clear existing objects.
    scene.camera = None
    for obj in scene.objects:
        scene.objects.unlink(obj)



    scene.unit_settings.system='METRIC'
    
    
    bpy.ops.import_scene.obj(filepath=obj_path, 
                             axis_forward='-Z', 
                             axis_up='Y', 
                             filter_glob="*.obj;*.mtl", 
                             use_edges=True, 
                             use_smooth_groups=True, 
                             use_split_objects=True, 
                             use_split_groups=True, 
                             use_groups_as_vgroups=False,
                             use_image_search=True,
                             split_mode='ON', 
                             global_clamp_size=0)
    
    
    
    #Get how to move all objects that they are completely centered
    minmax=getCurrentSceneMinMaxCoords()
    move=[0,0,0]    
    for a in range(3):
        move[a]=-(minmax[0][a]+(minmax[1][a]-minmax[0][a])/2)
    print("Centering move distance")
    print(move)
    
    
    
    #center scene
    for obj in bpy.context.scene.objects:
        obj.location.x=obj.location.x+move[0]
        obj.location.y=obj.location.y+move[1]
        obj.location.z=obj.location.z+move[2]
    
        #bpy.context.scene.cursor_location = pt
        
        pass
    bpy.context.scene.update()
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')    
    
    
    
    
    #Select all objects
    for obj in bpy.context.scene.objects:
        #rotate
        if(rot!=None):
            print(rot)
            rotateObjAroundCenter(obj, rot )
    
    
    bpy.context.scene.update()

    
    scales=[1.0, 1.0, 1.0]
    if(dimensions != None):
        scales=getScales(dimensions)
    ret_data['scales']=scales
    
    #get height over ground    
    minmax=getCurrentSceneMinMaxCoords()
    ret_data['elevate']=minmax[0][2]
        
    createDir(out_path+"/"+file_name)
    ret_data['model_file']="/"+file_name+"/"+file_name+".dae"
    out_file=out_path+ret_data['model_file']
    
    
    print("Converted Model: ", obj_path + " to " + out_file)
    
    
    #Export to collada file
    bpy.ops.wm.collada_export(filepath=out_file,
                              check_existing=True, 
                              filter_blender=False, 
                              filter_backup=False, 
                              filter_image=False, 
                              filter_movie=False, 
                              filter_python=False, 
                              filter_font=False, 
                              filter_sound=False, 
                              filter_text=False, 
                              filter_btx=False, 
                              filter_collada=True, 
                              filter_alembic=False,
                              filter_folder=True, 
                              filter_blenlib=False, 
                              filemode=8, 
                              display_type='DEFAULT', 
                              sort_method='FILE_SORT_ALPHA', 
                              apply_modifiers=False, 
                              export_mesh_type=0, 
                              export_mesh_type_selection='view', 
                              selected=False, 
                              include_children=False, 
                              include_armatures=False, 
                              include_shapekeys=True, 
                              deform_bones_only=False, 
                              active_uv_only=False, 
                              include_uv_textures=True, 
                              include_material_textures=True, 
                              use_texture_copies=True, 
                              triangulate=True, 
                              use_object_instantiation=True, 
                              use_blender_profile=True, 
                              sort_by_name=False, 
                              export_transformation_type=0, 
                              export_transformation_type_selection='matrix', 
                              open_sim=False)    
    return ret_data;


def convert_sh3d(obj_path, out_dir, ros_package=None):
    status=""
    
    mesh_dir_basename="/sh3d_catalog"
     
     #Create directories    
    def_out=createDir(out_dir+"/def")
    def_basic_out=createDir(out_dir+"/def/basic")
    launch_out=createDir(out_dir+"/launch")
    mesh_out=createDir(out_dir+mesh_dir_basename)
    model_out=createDir(out_dir+"/models")
    
    template_path=os.path.dirname(__file__)+"/../templates"
    
    
    shutil.copy(template_path+"/package_properties.xacro", def_basic_out)
    

    
    
    zip_ref = zipfile.ZipFile(obj_path, 'r')
    zip_ref.extractall(mesh_out)
    zip_ref.close()

    package_path=""
    if(ros_package!=None):
       out_dir=out_dir+"/"+ros_package
       

       
    header={}
    models={}
    
    

    #Lets read the FurnitureCatalog
    with open(mesh_out+"/"+"PluginFurnitureCatalog.properties",encoding='ISO-8859-1') as f:
        content = f.readlines()
    content = [x.strip() for x in content] 
        
    for line in content: 

        
        m_base=re.match("^([A-Za-z].*)=(.*)$",line)
        
        if(m_base != None):
            m_furniture=re.match("^([A-Za-z].*)#([0-9].*)",m_base.group(1))
            
            if(m_furniture==None): ##Is header
                header[m_base.group(1).lower()]=m_base.group(2)
                
            else: ##Is furniture
         
                if m_furniture.group(2) not in models.keys():
                    models[m_furniture.group(2)]={}
    
                models[m_furniture.group(2)][m_furniture.group(1).lower()]=m_base.group(2)
        
        
    
    

            
    for number, attributes in models.items():
        
        if(number != '427'):
            continue
    
        
        if "model" in attributes.keys():
            
            
            euler_angles=[0,0,0]
            model_path=mesh_out+attributes["model"]
            
            
            
            if os.path.exists(model_path):
                
                
                dimensions=[None,None,None]
                print(attributes.keys())
                
                if "width" in attributes.keys():
                    dimensions[0]=float(attributes["width"])/100
                
                if "depth" in attributes.keys():
                    dimensions[1]=float(attributes["depth"])/100
                        
                if "height" in attributes.keys():
                    dimensions[2]=float(attributes["height"])/100
                
                if "modelrotation" in attributes.keys():
                    r = [ float(rot) for rot in attributes["modelrotation"].split(" ")]
                    
                    
                    if(len(r)==9):
                        r11=r[0]
                        r21=r[3]
                        
                    
                        r31=r[6]
                        r32=r[7]
                        r33=r[8]
                    
                    
                        
                        
                        euler_angles[0]=atan2(r32,r33)
                        euler_angles[2]=atan2(-r31,sqrt(r32**2+r33**2))
                        euler_angles[1]=atan2(r21,r11)
                        

                        #convert to degrees
                        #for n, e in enumerate(euler_angles):
                        #    euler_angles[n]=e*180/pi
                        
                        print("EULER ANGLES:")
                        print(euler_angles)
                
                
                #get model_data    
                model_data=analyze_obj(model_path, model_out, dimensions, euler_angles)
                
                #get material path 
                model_file_name, extension = os.path.splitext(os.path.basename(model_path))

                #Write definition file
                def_file_template=template_path+"/template_simple.xacro"
                def_file_out = def_out+"/"+model_file_name+".xacro"
    
                #read template for main definition file 
                def_text=""
                with open(def_file_template) as f:
                    def_text=f.read()
                    f.close()
                
                #exchange template text
                def_text=def_text.replace('###SCALE_X###', str(model_data['scales'][0]))
                def_text=def_text.replace('###SCALE_Y###', str(model_data['scales'][1]))
                def_text=def_text.replace('###SCALE_Z###', str(model_data['scales'][2]))
                def_text=def_text.replace('###ELEVATION###', str(model_data['elevate']))
                
                
                def_text=def_text.replace('###MASS###', str(1.0))
                def_text=def_text.replace('###INERTIA_XX###', str(0.17))
                def_text=def_text.replace('###INERTIA_XY###', str(0))
                def_text=def_text.replace('###INERTIA_XZ###', str(0))
                def_text=def_text.replace('###INERTIA_YY###', str(0.17))
                def_text=def_text.replace('###INERTIA_YZ###', str(0))
                def_text=def_text.replace('###INERTIA_ZZ###', str(0.17))                                

                def_text=def_text.replace('###MESH_FILE###', "package://"+ros_package+"/"+os.path.basename(model_out)+model_data['model_file'])
                
                def_text=def_text.replace('###MODEL_NAME###', model_file_name )

                '''
                TODO remove meshfile add collisions
                '''
                def_text=def_text.replace('###SIMPLE_COLLISIONS###','<geometry><mesh filename="${meshfile}"/> </geometry>' )
                            
                
                #write out template
                with open(def_file_out, "w") as f:
                  f.write(def_text)




                
                
            else:
                status+=("Model does not exist: " +model_path+"\n")
        pass
        
    print("Conversion Status:")
    print("-------")
    print(status)



def main():
    import os
    import sys       # to get command line args
    import argparse  # to parse options for us and print a nice help message


    #variables

    # get the args passed to blender after "--", all of which are ignored by
    # blender so scripts may receive their own arguments
    argv = sys.argv

    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"

    # When --help or no args are given, print this help
    usage_text = (
            "Run blender in background mode with this script:"
            "  blender --background --python " + __file__ + " -- file_name out_path [options]"
            )
    #parser.add_option('--debug', action='store_true', dest='debug')


    parser = argparse.ArgumentParser(description=usage_text)

    # Example utility, add some text and renders or saves it (with options)
    # Possible types are: string, int, long, choice, float and complex.

    parser.add_argument('infile', help='input directory')
    parser.add_argument('outdir', help='output directory')
    parser.add_argument('--ros_package', help='name of package which should be created')
        
    args = parser.parse_args(argv)


    file_name, file_extension = os.path.splitext(args.infile)
    
    
    if(file_extension==".sh3f"):
        convert_sh3d(args.infile, args.outdir, args.ros_package)
        pass
    elif(file_extension==".obj"):
        analyze_obj(args.infile, args.outdir)
        pass
    else:
       raise TypeError("Unsupported file type! "+ file_extension)

    

    print("batch job finished, exiting")


if __name__ == "__main__":
    main()


