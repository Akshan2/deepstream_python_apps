#!/usr/bin/env python3

import sys
import gi
import pyds
sys.path.append(../)
gi.require_version('Gst', '1.0')
from gi.repository import Glib, Gst
from common.bus_call import bus_call
from common.is_aarch_64 import is_aarch64

def osd_sink_pad_buffer_probe(pad, info, u_data):
  
   gst_buffer = info.get_buffer()
   batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
   l_frame = batch_meta.frame_meta_list
   
   while l_frame is not None:
      try:
          frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
      except StopIteration:
          break
          
       frame_number = frame_meta.frame_num
       l_obj = frame_meta.obj_meta_list
        
        while l_obj is not None:
            try:
                obj_meta = pyds.NvDsObjectMeta(l_obj.data)
            except StopIteration:
                break
            
            bbox_data = obj_meta.detector_bbox_info
            print(bbox_data)
            
            try:
                l_obj=l_obj.next
            except StopIteration:
                break
                
        try:
            l_frame=l_frame.next
        except StopIteration:
            break

    return Gst.PadProbeReturn.OK	
        
def main():
    
    Gst.init(None)
    pipeline = Gst.Pipeline()
    src = Gst.ElementryFactory.make('filesrc', "filesource")
    parser = Gst.ElementFactory.make("h264parse", "h264-parser")
    decoder = Gst.ElementFactory.make("nvv4l2decoder", "nvv4l2-decoder")
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
            
     
