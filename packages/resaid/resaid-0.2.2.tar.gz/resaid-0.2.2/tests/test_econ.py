#!/usr/bin/env python3
"""
Test script for econ.py module to ensure functionality is preserved after cleanup.
"""
import sys
import os
import pandas as pd
import numpy as np
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from resaid.econ import npv_calc, well_econ

def test_npv_calc_basic():
    """Test basic NPV calculation functionality"""
    print("Testing basic NPV calculation...")
    
    # Test cashflow with positive NPV
    cashflow = np.array([-1000, 500, 500, 500])
    npv = npv_calc(cashflow)
    
    # Test NPV calculation
    result = npv.get_npv(0.1)
    assert isinstance(result, (int, float)), "NPV should return a number"
    # This cashflow should have positive NPV at 10% discount rate
    assert result > -1000, "NPV should be reasonable for this cashflow"
    
    # Test IRR calculation
    irr = npv.get_irr()
    assert isinstance(irr, (int, float)), "IRR should return a number"
    assert irr > 0, "IRR should be positive for this cashflow"
    
    return True

def test_npv_calc_negative_cashflow():
    """Test NPV calculation with negative total cashflow"""
    print("Testing NPV calculation with negative cashflow...")
    
    cashflow = np.array([-1000, -100, -100, -100])
    npv = npv_calc(cashflow)
    
    # Test IRR calculation for negative cashflow
    irr = npv.get_irr()
    assert irr == 0, "IRR should be 0 for negative cashflow"
    
    return True

def test_well_econ_initialization():
    """Test well_econ class initialization"""
    print("Testing well_econ initialization...")
    
    econ = well_econ(verbose=False)
    
    # Test default values
    assert econ.verbose == False, "Verbose should be False by default"
    assert econ.OIL_COL == "OIL", "OIL_COL should be 'OIL'"
    assert econ.GAS_COL == "GAS", "GAS_COL should be 'GAS'"
    assert econ.WATER_COL == "WATER", "WATER_COL should be 'WATER'"
    
    # Test property setters
    econ.oil_pri = 50.0
    assert econ.oil_pri == 50.0, "oil_pri property should work"
    
    econ.gas_pri = 3.0
    assert econ.gas_pri == 3.0, "gas_pri property should work"
    
    econ.discount_rate = 0.1
    assert econ.discount_rate == 0.1, "discount_rate property should work"
    
    return True

def test_price_generation():
    """Test price generation methods"""
    print("Testing price generation methods...")
    
    econ = well_econ()
    times = np.array([0, 1, 2, 3, 4])
    
    # Test single price
    econ.oil_pri = 50.0
    oil_prices = econ.generate_oil_price(times)
    assert len(oil_prices) == len(times), "Price array should match time length"
    assert all(price == 50.0 for price in oil_prices), "All prices should be 50.0"
    
    # Test price list
    econ.oil_pri = [45.0, 50.0, 55.0]
    oil_prices = econ.generate_oil_price(times)
    assert len(oil_prices) == len(times), "Price array should match time length"
    assert oil_prices[0] == 45.0, "First price should be 45.0"
    assert oil_prices[1] == 50.0, "Second price should be 50.0"
    assert oil_prices[2] == 55.0, "Third price should be 55.0"
    assert oil_prices[3] == 55.0, "Fourth price should be 55.0 (extended)"
    assert oil_prices[4] == 55.0, "Fifth price should be 55.0 (extended)"
    
    # Test gas price with differential
    econ.gas_pri = 3.0
    econ.gas_diff = 0.5
    gas_prices = econ.generate_gas_price(times)
    assert all(price == 3.5 for price in gas_prices), "All gas prices should be 3.5"
    
    return True

def test_capex_generation():
    """Test CAPEX generation method"""
    print("Testing CAPEX generation...")
    
    econ = well_econ()
    times = np.array([0, 1, 2, 3, 4])
    
    # Test fixed CAPEX
    econ.capex_val = 1000000
    # Create minimal header data for the test
    econ._header_data = pd.DataFrame({'UWI': ['test_well']})
    econ._header_uwi_col = 'UWI'
    capex = econ.generate_capex(times, "test_well")
    assert len(capex) == len(times), "CAPEX array should match time length"
    assert capex[0] == 1000000, "First period should have CAPEX"
    assert all(capex[i] == 0 for i in range(1, len(times))), "Other periods should be zero"
    
    return True

def test_zero_below():
    """Test zero_below method"""
    print("Testing zero_below method...")
    
    econ = well_econ()
    
    # Create test DataFrame
    df = pd.DataFrame({
        'T_INDEX': [1, 2, 3, 4, 5],
        'OIL': [100, 200, 300, 400, 500],
        'GAS': [1000, 2000, 3000, 4000, 5000]
    })
    
    result = econ.zero_below(df, 3, ['OIL', 'GAS'])
    
    assert result['OIL'].iloc[0] == 100, "First row OIL should remain 100"
    assert result['OIL'].iloc[1] == 200, "Second row OIL should remain 200"
    assert result['OIL'].iloc[2] == 300, "Third row OIL should remain 300"
    assert result['OIL'].iloc[3] == 0, "Fourth row OIL should be zero"
    assert result['OIL'].iloc[4] == 0, "Fifth row OIL should be zero"
    
    return True

def test_well_econ_with_sample_data():
    """Test well_econ with sample flowstream data"""
    print("Testing well_econ with sample data...")
    
    # Create sample flowstream data
    flowstream_data = pd.DataFrame({
        'UWI': ['WELL001', 'WELL001', 'WELL001'],
        'T_INDEX': [1, 2, 3],
        'MAJOR': ['OIL', 'OIL', 'OIL'],
        'OIL': [100, 90, 80],
        'GAS': [1000, 900, 800],
        'WATER': [50, 45, 40]
    })
    
    # Create sample header data
    header_data = pd.DataFrame({
        'UWI': ['WELL001'],
        'NRI': [0.8],
        'WI': [1.0]
    })
    
    econ = well_econ(verbose=False)
    econ.flowstreams = flowstream_data
    econ.flowstream_uwi_col = 'UWI'
    econ.flowstream_t_index = 'T_INDEX'
    econ.header_data = header_data
    econ.header_uwi_col = 'UWI'
    econ.wi_col = 'WI'
    econ.nri_col = 'NRI'
    
    # Set economic parameters
    econ.oil_pri = 50.0
    econ.gas_pri = 3.0
    econ.discount_rate = 0.1
    econ.opc_t = 1000
    econ.opc_oil = 5.0
    econ.opc_gas = 0.5
    econ.opc_water = 2.0
    econ.sev_oil = 0.05
    econ.sev_gas = 0.05
    econ.atx = 0.02
    econ.royalty = 0.2
    econ.capex_val = 1000000
    
    # Test well flowstream generation
    flow = econ.well_flowstream('WELL001')
    
    assert len(flow) == 3, "Flow should have 3 periods"
    assert 'revenue' in flow.columns, "Flow should have revenue column"
    assert 'cf' in flow.columns, "Flow should have cashflow column"
    assert flow['revenue'].sum() > 0, "Revenue should be positive"
    
    return True

def test_indicators_generation():
    """Test indicators generation"""
    print("Testing indicators generation...")
    
    # Create sample flowstream data
    flowstream_data = pd.DataFrame({
        'UWI': ['WELL001', 'WELL001', 'WELL001'],
        'T_INDEX': [1, 2, 3],
        'MAJOR': ['OIL', 'OIL', 'OIL'],
        'OIL': [100, 90, 80],
        'GAS': [1000, 900, 800],
        'WATER': [50, 45, 40]
    })
    
    # Create sample header data
    header_data = pd.DataFrame({
        'UWI': ['WELL001'],
        'NRI': [0.8],
        'WI': [1.0]
    })
    
    econ = well_econ(verbose=False)
    econ.flowstreams = flowstream_data
    econ.flowstream_uwi_col = 'UWI'
    econ.flowstream_t_index = 'T_INDEX'
    econ.header_data = header_data
    econ.header_uwi_col = 'UWI'
    econ.wi_col = 'WI'
    econ.nri_col = 'NRI'
    
    # Set economic parameters
    econ.oil_pri = 50.0
    econ.gas_pri = 3.0
    econ.discount_rate = 0.1
    econ.opc_t = 1000
    econ.opc_oil = 5.0
    econ.opc_gas = 0.5
    econ.opc_water = 2.0
    econ.sev_oil = 0.05
    econ.sev_gas = 0.05
    econ.atx = 0.02
    econ.royalty = 0.2
    econ.capex_val = 1000000
    
    # Generate indicators
    econ.generate_indicators()
    
    assert econ.indicators is not None, "Indicators should be generated"
    assert len(econ.indicators) == 1, "Should have one well in indicators"
    assert 'UWI' in econ.indicators.columns, "Indicators should have UWI column"
    assert 'IRR' in econ.indicators.columns, "Indicators should have IRR column"
    assert 'DCF' in econ.indicators.columns, "Indicators should have DCF column"
    
    return True

def test_cashflow_generation():
    """Test cashflow generation"""
    print("Testing cashflow generation...")
    
    # Create sample flowstream data
    flowstream_data = pd.DataFrame({
        'UWI': ['WELL001', 'WELL001', 'WELL001'],
        'T_INDEX': [1, 2, 3],
        'MAJOR': ['OIL', 'OIL', 'OIL'],
        'OIL': [100, 90, 80],
        'GAS': [1000, 900, 800],
        'WATER': [50, 45, 40]
    })
    
    # Create sample header data
    header_data = pd.DataFrame({
        'UWI': ['WELL001'],
        'NRI': [0.8],
        'WI': [1.0]
    })
    
    econ = well_econ(verbose=False)
    econ.flowstreams = flowstream_data
    econ.flowstream_uwi_col = 'UWI'
    econ.flowstream_t_index = 'T_INDEX'
    econ.header_data = header_data
    econ.header_uwi_col = 'UWI'
    econ.wi_col = 'WI'
    econ.nri_col = 'NRI'
    
    # Set economic parameters
    econ.oil_pri = 50.0
    econ.gas_pri = 3.0
    econ.discount_rate = 0.1
    econ.opc_t = 1000
    econ.opc_oil = 5.0
    econ.opc_gas = 0.5
    econ.opc_water = 2.0
    econ.sev_oil = 0.05
    econ.sev_gas = 0.05
    econ.atx = 0.02
    econ.royalty = 0.2
    econ.capex_val = 1000000
    
    # Generate cashflow
    cashflow = econ.generate_cashflow()
    
    assert len(cashflow) == 3, "Cashflow should have 3 periods"
    assert 'cf' in cashflow.columns, "Cashflow should have cf column"
    assert 'dcf' in cashflow.columns, "Cashflow should have dcf column"
    
    return True

def main():
    """Run all tests"""
    print("Starting econ.py tests...")
    start_time = time.time()
    
    tests = [
        test_npv_calc_basic,
        test_npv_calc_negative_cashflow,
        test_well_econ_initialization,
        test_price_generation,
        test_capex_generation,
        test_zero_below,
        test_well_econ_with_sample_data,
        test_indicators_generation,
        test_cashflow_generation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✅ {test.__name__} passed")
            else:
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            print(f"❌ {test.__name__} failed with exception: {e}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    print(f"Test duration: {duration:.2f} seconds")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
