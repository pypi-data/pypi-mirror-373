"""
Memory-efficient mzML to Parquet converter for large mass spectrometry files.

This module provides streaming conversion of mzML files to Parquet format
with minimal memory usage, suitable for processing large datasets.
"""

import base64
import struct
import zlib
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from typing import Iterator, Dict, Any, Optional
import gc
import os

def decode_binary_data(binary_element, cv_params):
    """Decode binary data from mzML format"""
    binary_data = binary_element.text.strip()
    decoded_bytes = base64.b64decode(binary_data)
    
    is_compressed = any(param.get('name') in ['zlib compression', 'gzip compression'] 
                       for param in cv_params)
    
    if is_compressed:
        decoded_bytes = zlib.decompress(decoded_bytes)
    
    data_type = None # "name"
    '''
Examples:
    Annotated mzML:
        <binaryDataArray encodedLength="1868">
        <cvParam cvRef="MS" accession="MS:1000595" name="time array" unitAccession="UO:0000010" unitName="second" unitCvRef="MS" />
        <cvParam cvRef="MS" accession="MS:1000523" name="64-bit float" />
        <cvParam cvRef="MS" accession="MS:1000576" name="no compression" />
        <binary>mpmZmZnzqkBSuB6Fa/qqQPYoXI9CAatArkfhehQIq0BSuB6F6w6rQArXo3C9FatAw/UoXI8cq0BmZmZmZiOrQB+F61E4KqtA16NwPQoxq0B7FK5H4TerQDMzMzOzPqtA16NwPYpFq0CPwvUoXEyrQEjhehQuU6tA7FG4HgVaq0CkcD0K12CrQEjhehSuZ6tAAAAAAIBuq0C4HoXrUXWrQFyPwvUofKtAFK5H4fqCq0C4HoXr0YmrQHE9CtejkKtAKVyPwnWXq0DNzMzMTJ6rQIXrUbgepatAKVyPwvWrq0DhehSux7KrQJqZmZmZuatAPQrXo3DAq0D2KFyPQserQK5H4XoUzqtAUrgehevUq0AK16NwvdurQK5H4XqU4qtAZmZmZmbpq0AfhetROPCrQMP1KFwP96tAexSuR+H9q0AzMzMzswSsQNejcD2KC6xAj8L1KFwSrEAzMzMzMxmsQOxRuB4FIKxApHA9CtcmrEBI4XoUri2sQAAAAACANKxAuB6F61E7rEBcj8L1KEKsQBSuR+H6SKxAuB6F69FPrEBxPQrXo1asQBSuR+F6XaxAzczMzExkrECF61G4HmusQClcj8L1caxA4XoUrsd4rECamZmZmX+sQD0K16NwhqxA9ihcj0KNrECamZmZGZSsQFK4HoXrmqxACtejcL2hrECuR+F6lKisQGZmZmZmr6xAH4XrUTi2rEDD9ShcD72sQHsUrkfhw6xAH4XrUbjKrEDXo3A9itGsQI/C9Shc2KxAMzMzMzPfrEDsUbgeBeasQKRwPQrX7KxASOF6FK7zrEAAAAAAgPqsQKRwPQpXAa1AXI/C9SgIrUAUrkfh+g6tQLgehevRFa1AcT0K16McrUAUrkfheiOtQM3MzMxMKq1AhetRuB4xrUApXI/C9TetQOF6FK7HPq1AhetRuJ5FrUA9CtejcEytQPYoXI9CU61AmpmZmRlarUBSuB6F62CtQPYoXI/CZ61ArkfhepRurUBmZmZmZnWtQArXo3A9fK1Aw/UoXA+DrUB7FK5H4YmtQB+F61G4kK1A16NwPYqXrUB7FK5HYZ6tQDMzMzMzpa1A7FG4HgWsrUCPwvUo3LKtQEjhehSuua1AAAAAAIDArUCkcD0KV8etQFyPwvUozq1AAAAAAADVrUC4HoXr0dutQHE9Ctej4q1AFK5H4XrprUDNzMzMTPCtQIXrUbge961AKVyPwvX9rUDhehSuxwSuQIXrUbieC65APQrXo3ASrkD2KFyPQhmuQJqZmZkZIK5AUrgehesmrkAK16NwvS2uQK5H4XqUNK5AZmZmZmY7rkAK16NwPUKuQMP1KFwPSa5AZmZmZuZPrkAfhetRuFauQNejcD2KXa5AexSuR2FkrkAzMzMzM2uuQOxRuB4Fcq5Aj8L1KNx4rkBI4XoUrn+uQOxRuB6Fhq5ApHA9CleNrkBcj8L1KJSuQAAAAAAAm65AuB6F69GhrkBxPQrXo6iuQBSuR+F6r65AzczMzEy2rkBxPQrXI72uQClcj8L1w65A4XoUrsfKrkCF61G4ntGuQD0K16Nw2K5A9ihcj0LfrkCamZmZGeauQFK4HoXr7K5A9ihcj8LzrkCuR+F6lPquQGZmZmZmAa9ACtejcD0Ir0DD9ShcDw+vQHsUrkfhFa9AH4XrUbgcr0DXo3A9iiOvQHsUrkdhKq9AMzMzMzMxr0DsUbgeBTivQI/C9SjcPq9ASOF6FK5Fr0AAAAAAgEyvQKRwPQpXU69AXI/C9Shar0AAAAAAAGGvQLgehevRZ69AcT0K16Nur0AUrkfhenWvQM3MzMxMfK9AhetRuB6Dr0ApXI/C9YmvQOF6FK7HkK9AhetRuJ6Xr0A=</binary>
    </binaryDataArray>
    <binaryDataArray encodedLength="936">
        <cvParam cvRef="MS" accession="MS:1000515" name="intensity array" unitAccession="MS:1000131" unitName="number of counts" unitCvRef="MS"/>
        <cvParam cvRef="MS" accession="MS:1000521" name="32-bit float" />
        <cvParam cvRef="MS" accession="MS:1000576" name="no compression" />
        <binary>AABIQgAAtEIAAKBCAAAWQwAASEMAACpDAADIQgAA8EIAAAJDAADwQgAAtEIAAHBCAAC0QgAAcEIAAMhCAAAgQgAAoEIAAPBBAABIQgAAoEIAAKBCAADwQQAA8EEAAIxCAABIQgAAoEIAAHBCAACgQQAAtEIAANxCAADIQgAASEIAAEhCAABwQgAAjEIAAEhCAABwQgAASEIAAKBCAACMQgAASEIAALRCAAA+QwAAKkMAADRDAAC0QgAAIEIAAKBCAACMQgAAIEIAAPBBAABIQgAAIEIAACBCAAAgQgAAjEIAAPBBAACgQQAAoEEAAPBBAAAgQgAAcEIAAIxCAACgQgAAyEIAACBCAABIQgAAtEIAAEhCAABIQgAAIEIAAMhCAAAMQwAAh0MAgJtDAABcQwCAkUMAAIdDAABcQwAANEMAABZDAACMQgAAjEIAAIxCAACMQgAAyEIAAEhCAABwQgAAIEEAAKBBAACgQQAAcEIAAPBBAACgQQAAoEIAAHBCAABIQgAA8EEAAEhCAACgQgAAIEIAAKBBAADwQQAAjEIAAEhCAACgQQAAIEIAACBCAACgQQAA8EEAAKBCAAC0QgAANEMAANxCAACHQwAANEMAAAJDAAACQwAAAkMAAHBCAAC0QgAAjEIAAKBCAACMQgAA8EIAAMhCAADwQQAASEIAAEhCAAAgQgAASEIAAPBBAACgQgAASEIAAEhCAADwQQAAtEIAALRCAABIQgAAjEIAAEhCAAAgQgAASEIAAPBBAAAgQgAA3EIAACBDAAAXQwAAAkMAAIxCAACgQgAAoEEAALRCAAAgQgAAyEIAAEhCAADIQgAAyEIAAKBCAAC0QgAAjEIAAPBBAACgQgAAoEEAAHBCAAAgQgAAjEIAALRCAABwQgAAoEIAAHBCAADwQgAAoEIAACBDAACCQw==</binary>
    </binaryDataArray>

    Another mzML:
    <binaryDataArray arrayLength="5625" encodedLength="624">
        <cvParam cvRef="MS" accession="MS:1000522" name="64-bit integer" value=""/>
        <cvParam cvRef="MS" accession="MS:1000574" name="zlib compression" value=""/>
        <cvParam cvRef="MS" accession="MS:1000786" name="non-standard data array" value="ms level" unitCvRef="UO" unitAccession="UO:0000186" unitName="dimensionless unit"/>
        <binary>eJzt2cFShDAMAFDx/z96D3qRGQZoGpLi85LRfds2IbS7sn39/Hz/xm33+1ncmsSj9cxa593xV6nPKrFLnaPz3X1/dn5n41+dv7q/jvalq31z9/3d7r/q+q9y/90dP6sfutevOs/o54xZea5SL/FvzLoe1f2gz94RXcfa+LZzfZW+nHXedskv+zx4y/febn1c3YfiWOz6/0cxJ656nVdd91P5Z3+v73pdu3zurK5jt75atV5d+um/RPVdO3Z7/laV59nzrqvP/Xme53me53me53me53me53me53me53me53me53me53me53me53me53me53me53me53me53me53me53me53me53me53me53me53me53me53me57N81ryz3Wp+//enr9fsvKOvV/Vvl3mu9kNVntG+Ohuv+r6tnn90vfuYvZ7s+6XLuTUr39Fxo3WLjp/dr1nrvnp/jI4T3Vee2qej+/DsOmT39az+i/btaP2idcxa39H7rsa7/TOax+x1R/fB7LqN7jtZdRq9f56q8+h5UTXe6HWM7vPRfGbt+9H9OeucjJ5fWed+1Ge/np3nrHOzW17dfJd1zPKj/XDXjc4b3Vd4nud5nud5nuer/Qdh7yS7</binary>
    </binaryDataArray>

    '''
    for param in cv_params:
        name = param.get('name', '')
        if '64-bit float' in name:
            data_type = 'd'
        elif '32-bit float' in name:
            data_type = 'f'
        elif '64-bit integer' in name:
            data_type = 'q'
        elif '32-bit integer' in name:
            data_type = 'i'
    
    if data_type is None:
        data_type = 'f'
    
    # Unpack (https://docs.python.org/3/library/struct.html)
    num_values = len(decoded_bytes) // struct.calcsize(data_type)
    values = struct.unpack('<' + data_type * num_values, decoded_bytes)
    
    return np.array(values)

def iter_spectra_streaming(file_path: str, chunk_size: int = 1000) -> Iterator[Dict[str, Any]]:
    """
    Stream spectra from mzML file in chunks to minimize memory usage.
    
    Args:
        file_path: Path to mzML file
        chunk_size: Number of spectra to process in each chunk
        
    Yields:
        Dictionary containing spectrum data
    """
    ns = {'mz': 'http://psi.hupo.org/ms/mzml'}
    
    # Use iterparse for memory-efficient XML parsing
    context = ET.iterparse(file_path, events=("start", "end"))
    context = iter(context)
    event, root = next(context)
    
    spectrum_count = 0
    
    for event, elem in context:
        if event == "end" and elem.tag.endswith("}spectrum"):
            spectrum_data = process_spectrum_element(elem, ns)
            if spectrum_data:
                yield spectrum_data
                spectrum_count += 1
            
            # Clear processed element to free memory
            elem.clear()
            root.clear()
            
            # Force garbage collection periodically
            if spectrum_count % chunk_size == 0:
                gc.collect()


def process_spectrum_element(spectrum_elem, ns: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Process a single spectrum element and return data rows"""
    spectrum_id = spectrum_elem.get('id', '')
    spectrum_index = spectrum_elem.get('index', '')
    
    ms_level = 1
    ms_level_param = spectrum_elem.find('.//mz:cvParam[@name="ms level"]', ns)
    if ms_level_param is not None:
        ms_level = int(ms_level_param.get('value', 1))
    
    scan_time = None
    scan_time_param = spectrum_elem.find('.//mz:cvParam[@name="scan start time"]', ns)
    if scan_time_param is not None:
        scan_time = float(scan_time_param.get('value', 0))
        unit = scan_time_param.get('unitName', '')
        if 'minute' in unit:
            scan_time *= 60
    
    precursor_mz = None
    if ms_level > 1:
        precursor_list = spectrum_elem.find('.//mz:precursorList', ns)
        if precursor_list is not None:
            precursor = precursor_list.find('.//mz:precursor', ns)
            if precursor is not None:
                isolation_window = precursor.find('.//mz:isolationWindow', ns)
                if isolation_window is not None:
                    target_mz_param = isolation_window.find('.//mz:cvParam[@name="isolation window target m/z"]', ns)
                    if target_mz_param is not None:
                        precursor_mz = float(target_mz_param.get('value', 0))
    
    binary_arrays = spectrum_elem.findall('.//mz:binaryDataArray', ns)
    mz_array = None
    intensity_array = None
    
    for binary_array in binary_arrays:
        cv_params = binary_array.findall('.//mz:cvParam', ns)
        
        array_type = None
        for param in cv_params:
            name = param.get('name', '')
            if 'm/z array' in name:
                array_type = 'mz'
            elif 'intensity array' in name:
                array_type = 'intensity'
        
        binary_element = binary_array.find('.//mz:binary', ns)
        if binary_element is not None and binary_element.text:
            decoded_data = decode_binary_data(binary_element, cv_params)
            
            if array_type == 'mz':
                mz_array = decoded_data
            elif array_type == 'intensity':
                intensity_array = decoded_data
    
    if mz_array is not None and intensity_array is not None:
        return {
            'spectrum_id': spectrum_id,
            'spectrum_index': spectrum_index,
            'ms_level': ms_level,
            'scan_time': scan_time,
            'precursor_mz': precursor_mz,
            'mz_array': mz_array,
            'intensity_array': intensity_array
        }
    
    return None


def write_spectrum_parquet(file_path: str, output_path: str, batch_size: int, compression: str):
    """Write spectrum data to Parquet file in batches"""
    
    # Define schema
    schema = pa.schema([
        pa.field('spectrum_id', pa.string()),
        pa.field('spectrum_index', pa.string()),
        pa.field('ms_level', pa.int32()),
        pa.field('scan_time', pa.float64()),
        pa.field('point_index', pa.int32()),
        pa.field('mz', pa.float64()),
        pa.field('intensity', pa.float64()),
        pa.field('precursor_mz', pa.float64()),
        pa.field('product_mz', pa.float64()),
        pa.field('peptide_sequence', pa.string())
    ])
    
    with pq.ParquetWriter(output_path, schema, compression=compression) as writer:
        batch_data = []
        total_points = 0
        
        for spectrum_data in iter_spectra_streaming(file_path):
            mz_array = spectrum_data['mz_array']
            intensity_array = spectrum_data['intensity_array']
            
            for i, (mz_val, intensity_val) in enumerate(zip(mz_array, intensity_array)):
                row = {
                    'spectrum_id': spectrum_data['spectrum_id'],
                    'spectrum_index': spectrum_data['spectrum_index'],
                    'ms_level': spectrum_data['ms_level'],
                    'scan_time': spectrum_data['scan_time'],
                    'point_index': i,
                    'mz': float(mz_val),
                    'intensity': float(intensity_val),
                    'precursor_mz': spectrum_data['precursor_mz'],
                    'product_mz': float(mz_val) if spectrum_data['ms_level'] > 1 else None,
                    'peptide_sequence': None
                }
                batch_data.append(row)
                total_points += 1
                
                if len(batch_data) >= batch_size:
                    # Write batch to Parquet
                    df_batch = pd.DataFrame(batch_data)
                    table = pa.Table.from_pandas(df_batch, schema=schema)
                    writer.write_table(table)
                    
                    # Clear batch and force garbage collection
                    batch_data.clear()
                    del df_batch, table
                    gc.collect()
                    
                    print(f"Processed {total_points} data points...")
        
        # Write remaining data
        if batch_data:
            df_batch = pd.DataFrame(batch_data)
            table = pa.Table.from_pandas(df_batch, schema=schema)
            writer.write_table(table)
            del df_batch, table
        
        print(f"Total data points processed: {total_points}")


def write_chromatogram_parquet(file_path: str, output_path: str, batch_size: int, compression: str):
    """Write chromatogram data to Parquet file in batches - placeholder for chromatogram support"""
    print("Chromatogram processing not yet implemented in streaming version")
    

def convert_mzml_to_parquet_streaming(file_path: str, output_path: Optional[str] = None, 
                                    batch_size: int = 10000, compression: str = 'snappy') -> str:
    """
    Convert mzML file to Parquet format using streaming for memory efficiency.
    
    Args:
        file_path: Path to input mzML file
        output_path: Path for output Parquet file (optional)
        batch_size: Number of data points to process in each batch
        compression: Parquet compression type ('snappy', 'gzip', 'lz4', 'brotli')
        
    Returns:
        Path to the created Parquet file
    """
    if output_path is None:
        # Handle both .mzML and .mzml extensions
        if file_path.lower().endswith('.mzml'):
            output_path = file_path[:-5] + '_converted.parquet'
        else:
            output_path = file_path + '_converted.parquet'
    
    # Check if file has chromatograms or spectra by doing a quick scan
    has_chromatograms = check_for_chromatograms(file_path)
    
    if has_chromatograms:
        print("Processing chromatogram data...")
        write_chromatogram_parquet(file_path, output_path, batch_size, compression)
    else:
        print("Processing spectrum data...")
        write_spectrum_parquet(file_path, output_path, batch_size, compression)
    
    print(f"Conversion complete: {output_path}")
    return output_path


def check_for_chromatograms(file_path: str) -> bool:
    """Quick check to see if file contains chromatogram data"""
    try:
        context = ET.iterparse(file_path, events=("start", "end"))
        for event, elem in context:
            if event == "end" and elem.tag.endswith("}chromatogram"):
                return True
            elif event == "end" and elem.tag.endswith("}spectrum"):
                # If we find a spectrum first, assume it's spectrum data
                return False
        return False
    except:
        return False


def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get basic information about the mzML file without loading it fully"""
    file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
    
    # Quick scan for basic info
    has_chromatograms = check_for_chromatograms(file_path)
    
    return {
        'file_size_mb': round(file_size, 2),
        'data_type': 'chromatogram' if has_chromatograms else 'spectrum',
        'recommended_batch_size': min(50000, max(5000, int(100000 / max(1, file_size / 100))))
    }


# Example usage
if __name__ == "__main__":
    # Example usage with memory-efficient processing
    file_path = "TMT.mzML"
    
    # Get file info first
    info = get_file_info(file_path)
    print(f"File info: {info}")
    
    # Convert with appropriate batch size based on file size
    output_file = convert_mzml_to_parquet_streaming(
        file_path, 
        batch_size=info['recommended_batch_size'],
        compression='snappy'
    )
    
    print(f"Conversion completed: {output_file}")