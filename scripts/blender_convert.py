import bpy,bmesh
import os
import zipfile
import tempfile
import os, shutil
import re
import io


from copy import copy
from numpy.f2py.crackfortran import dimensionpattern
from builtins import enumerate
from debian.copyright import Header

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
    scales=[0,0,0]
    sizes=[0,0,0]
    for s in range(3):
        sizes[s]=minmax[1][s]-minmax[0][s]
        
        
    for s in range(3):
        if(abs(sizes[s] - target_sizes[s]) >0.001):
            scales=target_sizes[s]/sizes[s]
    pass

    return scales

def convert_obj(obj_path, out_path, dimensions=None):
    file_name, file_extension = os.path.splitext(os.path.basename(obj_path))
    scene = bpy.context.scene
    out_file=out_path+"/"+file_name+".dae"
 
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
    floor=minmax[0][2]

    scales=[1.0, 1.0, 1.0]
    if(dimensions != None):
        scales=getScales(dimensions)

    print("Converted Model: ", obj_path + " to " + out_file)
    print("Model should be scaled  in [x,y,z] like " + str(scales))
    print("According to vertex information it should be positioned " + str(floor) + " meters above floor in Gazebo, to not get stuck")
    
    

        
    
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
    pass

def convert_sh3d(obj_path, out_dir):
    tempfolder=tempfile.mkdtemp()
    print(tempfolder)
    
    zip_ref = zipfile.ZipFile(obj_path, 'r')
    zip_ref.extractall(tempfolder)
    zip_ref.close()

    header_tags=list(enumerate([
        "modified",
        "id",
        "name",
        "description",
        "version",
        "license ",
        "provider"
    ]))
    
    furniture_tags=list(enumerate([
    "id",#0
    "name",
    "description",
    "information",
    "tags",
    "creation_date",
    "grade",
    "category",
    "creator",
    "price",
    "value_added_tax_percentage",#10
    "model",
    "icon",
    "plan_icon",
    "width",#14
    "depth",#15
    "height",#16
    "movable",#17
    "door_or_window",
    "door_or_window_cut_out_shape",
    "staircase_cut_out_shape",
    "elevation",#21
    "model_rotation",#22
    "resizable",#23
    "deformable",
    "texturable"
    ]))
    
    processing_tags=[11,14,15,16,17,21,22,23]
    info_tags=[0,1,2,3,4,5,7,8,9]


    header={}
    models={}
    model=0
    
    

    #Lets read the FurnitureCatalog
    with open(tempfolder+"/"+"PluginFurnitureCatalog.properties",encoding='ISO-8859-1') as f:
        content = f.readlines()
    content = [x.strip() for x in content] 
        
    for line in content: 
        hashFound=line.find("#")
        if(model==0):
            if(hashFound==0): #Comment
                continue
            elif(hashFound>0): #Models section started
                model=1
            else: #file header
                #line.lower().match()
                pass
        if(model>0):
             
             
            pass
    
    shutil.rmtree(tempfolder)
    pass
    



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

    parser.add_argument('infile')
    parser.add_argument('outdir')
    args = parser.parse_args(argv)  # In this example we wont use the args

    file_name, file_extension = os.path.splitext(args.infile)
    

    if(file_extension==".sh3f"):
        convert_sh3d(args.infile, args.outdir)
        pass
    elif(file_extension==".obj"):
        convert_obj(args.infile, args.outdir)
        pass
    else:
       raise TypeError("Unsupported file type! "+ file_extension)

    

    print("batch job finished, exiting")


if __name__ == "__main__":
    main()


