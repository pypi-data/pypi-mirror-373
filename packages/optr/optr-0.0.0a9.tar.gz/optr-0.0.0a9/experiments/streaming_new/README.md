# Streaming Primitives Experiments

This directory contains experiments to test the streaming primitives built with the optr framework.

## What Works ✅

- **Basic imports and creation**: All streaming components can be imported and instantiated
- **FPS handling**: FPS objects work correctly and convert to proper GStreamer format
- **Caps generation**: Video caps are generated correctly and match expected format
- **Raw GStreamer**: Basic GStreamer pipelines work when constructed manually

## What Needs Work ❌

- **Pipeline state management**: Pipelines fail to reach PLAYING state (ret=2, current=3)
- **Writer classes**: FileWriter, SHMWriter fail during pipeline initialization
- **Reader classes**: TestPatternReader has pixel format issues in buffer.pull()

## Files Created

### Working Examples
- `minimal_test.py` - Raw GStreamer test that works
- `debug_caps.py` - Caps generation test (works)
- `final_test.py` - Comprehensive test suite

### Problematic Examples  
- `simple_producer.py` - Uses SHMWriter (fails)
- `simple_consumer.py` - Uses SHMReader (fails)
- `simple_producer_file.py` - Uses FileWriter (fails)
- `test_reader.py` - Uses TestPatternReader (fails)
- `working_producer.py` - Raw GStreamer with memory issues

## Key Issues Identified

1. **Pipeline State**: GStreamer pipelines created by the abstraction layer fail to reach PLAYING state
2. **Buffer Format**: TestPatternReader produces UNKNOWN pixel format instead of RGB
3. **Element Linking**: Possible issues in how elements are linked in the pipeline abstraction

## Next Steps

To make the streaming primitives fully functional:

1. Debug why pipelines fail to reach PLAYING state
2. Fix the buffer format negotiation in TestPatternReader
3. Ensure proper element linking in pipeline.chain()
4. Add error handling and debugging to control.play_sync()

## Usage

Run the comprehensive test:
```bash
python final_test.py
```

Run individual tests:
```bash
python minimal_test.py      # Raw GStreamer (works)
python debug_caps.py        # Caps generation (works)
python test_reader.py       # TestPatternReader (fails)
```

## Architecture

The streaming primitives provide a clean abstraction over GStreamer:

```
TestPatternReader → SHMWriter → /tmp/socket → SHMReader → Display
     (Producer)                                  (Consumer)
```

The core components are:
- **Readers**: TestPatternReader, SHMReader, FileReader, RTMPReader, UDPReader
- **Writers**: SHMWriter, FileWriter, RTMPWriter, UDPWriter  
- **Protocols**: Reader[T], Writer[T], Closer for clean interfaces
- **Utilities**: FPS, caps, buffer, control, pipeline modules
