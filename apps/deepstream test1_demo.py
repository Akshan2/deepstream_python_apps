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
    transform = Gst.ElementFactory.make("nvegltransform", "nvegl-transform")
    sink = Gst.ElementFactory.make("nveglglessink", "nvvideo-renderer")
    pgie.set_property('config-file-path', "dstest1_pgie_config.txt")
    
    pipeline.add(source)
    pipeline.add(h264parser)
    pipeline.add(decoder)
    pipeline.add(streammux)
    pipeline.add(pgie)
    pipeline.add(nvvidconv)
    pipeline.add(nvosd)
    pipeline.add(sink)
    pipeline.add(transform)
    
    sinkpad = streammux.get_request_pad("sink_0")
    srcpad = decoder.get_static_pad("src")
    
    source.link(h264parser)
    h264parser.link(decoder)
    srcpad.link(sinkpad)
    streammux.link(pgie)
    pgie.link(nvvidconv)
    nvvidconv.link(nvosd)
    nvosd.link(transform)
    transform.link(sink)
    
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect ("message", bus_call, loop)
    
    osdsinkpad = nvosd.get_static_pad("sink")
    osdsinkpad.add_probe(Gst.PadProbeType.BUFFER, osd_sink_pad_buffer_probe, 0)
    
    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except:
        pass
    pipeline.set_state(Gst.State.NULL)
    
if __name__ == '__main__':
    sys.exit(main(sys.argv))
            
     
