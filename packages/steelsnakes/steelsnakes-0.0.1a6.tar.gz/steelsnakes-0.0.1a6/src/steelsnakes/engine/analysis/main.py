# import ctypes
# import json
# # import numpy as np # TODO: will add...
# # import polars as pl # TODO: will add...

# from steelsnakes.UK.universal import UB, UniversalBeam

# # Import our Go FFI wrapper
# try:
#     from cgo_lib.cgo_ffi import SteelCalculatorFFI, calculate_steel_moment # type: ignore
#     HAS_GO_FFI = True
# except (ImportError, FileNotFoundError) as e:
#     print(f"Go FFI not available: {e}")
#     print("Run 'make build' in this directory to enable Go calculations")
#     HAS_GO_FFI = False
#     calculate_steel_moment = None  # type: ignore


# def main() -> None:
#     # TODO: considered stripping designation on creation, but no, that's left to the user/developer, so the TODO: is to notify them
#     # ... kind of like Zig's creator and private fields: he said NOPE
#     beam: UniversalBeam = UB(designation="762x267x197") # TODO: implement random/test/first beam/element per regional library/element
#     print("=== Steel Section Analysis ===")
#     print(f"Section: {beam.designation}")
    
#     # Get properties from steelsnakes
#     properties = beam.get_properties() # TODO: implement .properties property for everything and .dimensions property for just dimensions (maybe not)
#     print("\nSection Properties:")
#     print(json.dumps(properties, indent=2))
    
#     # Traditional Python calculation
#     M_Rd_python = beam.W_el_yy * 355 * 1000 # Convert to Nmm (cm³ * N/mm² * 1000 = Nmm)
#     print(f"\nPython calculation - M_Rd = {M_Rd_python:,.0f} Nmm")
    
#     # Demonstrate Go FFI calculation (if available)
#     if HAS_GO_FFI:
#         print("\n=== Go FFI Demonstration ===")
        
#         # Prepare data for Go function
#         section_data = {
#             "designation": beam.designation,
#             "W_el_yy": beam.W_el_yy,
#             "W_pl_yy": getattr(beam, 'W_pl_yy', beam.W_el_yy * 1.12),  # Estimate if not available
#             "fy": 355.0,  # N/mm² - could come from material properties
#             "h": beam.h,
#             "b": beam.b
#         }
#         try:
#             # Call Go function via FFI
#             if calculate_steel_moment is None:
#                 raise RuntimeError("Go FFI not available")
#             go_result = calculate_steel_moment(275, section_data) # FIXME: fy, no import,
#             go_result = calculate_steel_moment(275, section_data)
#             print("Go FFI calculation successful!")
#             print(json.dumps(go_result, indent=2))
            
#             # Compare results
#             python_result = M_Rd_python
#             go_result_mrd = go_result.get('M_Rd', 0)
#             difference = abs(python_result - go_result_mrd)
#             print(f"\nComparison:")  # noqa: F541
#             print(f"Python M_Rd: {python_result:,.0f} Nmm")
#             print(f"Go FFI M_Rd: {go_result_mrd:,.0f} Nmm")
#             print(f"Difference:  {difference:,.0f} Nmm")
            
#             # Demonstrate bulk analysis
#             test_bulk_analysis()
            
#         except Exception as e:
#             print(f"Go FFI calculation failed: {e}")
    
#     # TODO: implement .W_pl_yy property
#     # TODO: implement .W_el_zz property
#     # TODO: implement .W_pl_zz property
#     # TODO: implement .W_eff_yy property
#     # TODO: implement .W_eff_zz property


# def test_bulk_analysis():
#     """Demonstrate bulk section analysis using Go FFI."""
#     if not HAS_GO_FFI:
#         return
    
#     print("\n=== Bulk Analysis Demo ===")
    
#     # Create test data for multiple sections
#     test_sections = [
#         {
#             "designation": "457x191x67",
#             "W_el_yy": 1440.0,
#             "W_pl_yy": 1610.0,
#             "fy": 355.0,
#             "h": 457.0,
#             "b": 191.0
#         },
#         {
#             "designation": "533x210x82", 
#             "W_el_yy": 2120.0,
#             "W_pl_yy": 2380.0,
#             "fy": 355.0,
#             "h": 533.0,
#             "b": 210.0
#         },
#         {
#             "designation": "762x267x197",
#             "W_el_yy": 6420.0,
#             "W_pl_yy": 7200.0,
#             "fy": 355.0,
#             "h": 762.0,
#             "b": 267.0
#         }
#     ]
    
#     try:
#         from cgo_lib. import analyze_multiple_sections, find_optimal_section
        
#         # Bulk analysis
#         bulk_results = analyze_multiple_sections(test_sections)
#         print("Bulk analysis results:")
#         for i, result in enumerate(bulk_results):
#             section = test_sections[i]
#             print(f"  {section['designation']}: M_Rd = {result['M_Rd']:,.0f} Nmm, "
#                   f"Util = {result['util_ratio']:.2f}")
        
#         # Optimization demo
#         required_moment = 500_000_000  # 500 kNm in Nmm
#         optimization_result = find_optimal_section(
#             required_moment, test_sections, max_depth=600.0
#         )
        
#         print(f"\nOptimization for {required_moment:,.0f} Nmm:")
#         if 'optimal_section' in optimization_result:
#             print(f"  Optimal section: {optimization_result['optimal_section']}")
#             print(f"  Utilization: {optimization_result['utilization']:.2f}")
#         else:
#             print(f"  {optimization_result.get('error', 'No solution found')}")
            
#     except Exception as e:
#         print(f"Bulk analysis failed: {e}")

# if __name__ == "__main__":
#     main()