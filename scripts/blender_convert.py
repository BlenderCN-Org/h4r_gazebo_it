import bpy,bmesh
import os
import zipfile
import tempfile
import os, shutil
import re
import io
from copy import copy

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
    
    
    
    for s in range(3):
        sizes[s]=minmax[1][s]-minmax[0][s]
            
    for s in range(3):
        if(target_sizes[s]!=None):
            if(abs(sizes[s] - target_sizes[s]) >0.001):
                scales[s]=target_sizes[s]/sizes[s]
                
    return scales

def analyze_obj(obj_path, out_path, dimensions=None):
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
    
    
    #Select all objects
    for obj in bpy.context.scene.objects:
        obj.select = True
    
    #get height over ground    
    minmax=getCurrentSceneMinMaxCoords()
    ret_data['elevate']=minmax[0][2]

    
    scales=[1.0, 1.0, 1.0]
    if(dimensions != None):
        scales=getScales(dimensions)
    ret_data['scales']=scales
    
    
    
    
    
        
    return ret_data;


def convert_sh3d(obj_path, out_dir, ros_package=None):
    tempfolder=tempfile.mkdtemp()
    #print(tempfolder)
    #print(ros_package)
    
    
    
    zip_ref = zipfile.ZipFile(obj_path, 'r')
    zip_ref.extractall(tempfolder)
    zip_ref.close()

    package_path=""
    if(ros_package!=None):
       out_dir=out_dir+"/"+ros_package

    #Create directories    
    def_out=createDir(out_dir+"/def")
    def_basic_out=createDir(out_dir+"/def/basic")
    launch_out=createDir(out_dir+"/launch")
    mesh_out=createDir(out_dir+"/mesh")
    model_out=createDir(out_dir+"/models")
    
    template_path=os.path.dirname(__file__)+"/../templates"
    
    
    shutil.copy(template_path+"/package_properties.xacro", def_basic_out)
        
    header={}
    models={}
    
    

    #Lets read the FurnitureCatalog
    with open(tempfolder+"/"+"PluginFurnitureCatalog.properties",encoding='ISO-8859-1') as f:
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
        
        if "model" in attributes.keys():
            
            model_path=tempfolder+attributes["model"]
            
            if os.path.exists(model_path):
                
                
                dimensions=[None,None,None]
                
                if "length" in attributes.keys():
                    dimensions[0]=float(attributes["length"])
                
                if "width" in attributes.keys():
                    dimensions[1]=float(attributes["width"])
                        
                if "height" in attributes.keys():
                    dimensions[2]=float(attributes["height"])
                
                #get model_data    
                model_data=analyze_obj(model_path, model_out, dimensions)
                
                #get material path 
                material_path, extension = os.path.splitext(model_path)
                material_path+=".mtl"
                
                print(material_path)
                
                
                
                break ###TODO <---REMOVE THIS LINE---
                
            else:
                status+=("Model does not exist: " +model_path+"\n")
        pass
        
    print("Conversion Status:")
    print("-------")
    print(status)
        

    shutil.rmtree(tempfolder)

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


