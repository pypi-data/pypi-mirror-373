#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('..'))

from klotho.tonos.systems.combination_product_sets import Hexany, Eikosany, match_pattern

def test_case_1():
    """Test case 1: hx = Hexany(), pattern = [0,2,5]"""
    print("Testing case 1...")
    hx = Hexany()
    result = match_pattern(hx, [0, 2, 5])
    
    expected = {(0, 2, 3), (0, 3, 4), (1, 2, 5), (1, 3, 4), (1, 4, 5)}
    actual = {tuple(sorted(match)) for match in result}
    
    print(f"Expected: {sorted(expected)}")
    print(f"Actual:   {sorted(actual)}")
    
    assert actual == expected, f"Test case 1 failed!\nExpected: {sorted(expected)}\nActual: {sorted(actual)}\nMissing: {sorted(expected - actual)}\nExtra: {sorted(actual - expected)}"

def test_case_2():
    """Test case 2: hx = Hexany(), pattern = [0,3,1,5]"""
    print("\nTesting case 2...")
    hx = Hexany()
    result = match_pattern(hx, [0, 3, 1, 5])
    
    expected = {(0, 1, 2, 4), (2, 3, 4, 5)}
    actual = {tuple(sorted(match)) for match in result}
    
    print(f"Expected: {sorted(expected)}")
    print(f"Actual:   {sorted(actual)}")
    
    assert actual == expected, f"Test case 2 failed!\nExpected: {sorted(expected)}\nActual: {sorted(actual)}\nMissing: {sorted(expected - actual)}\nExtra: {sorted(actual - expected)}"

def test_case_3():
    """Test case 3: hx = Hexany(), pattern = [2,0,5,4]"""
    print("\nTesting case 3...")
    hx = Hexany()
    result = match_pattern(hx, [2, 0, 5, 4])
    
    expected = {(1, 2, 3, 4), (1, 2, 3, 5), (0, 1, 4, 5), (0, 3, 4, 5), (0, 1, 2, 3)}
    actual = {tuple(sorted(match)) for match in result}
    
    print(f"Expected: {sorted(expected)}")
    print(f"Actual:   {sorted(actual)}")
    
    assert actual == expected, f"Test case 3 failed!\nExpected: {sorted(expected)}\nActual: {sorted(actual)}\nMissing: {sorted(expected - actual)}\nExtra: {sorted(actual - expected)}"

def test_case_4():
    """Test case 4: hx = Hexany(), pattern = [2,3,1]"""
    print("\nTesting case 4...")
    hx = Hexany()
    result = match_pattern(hx, [2, 3, 1])
    
    expected = {(0, 4, 5)}
    actual = {tuple(sorted(match)) for match in result}
    
    print(f"Expected: {sorted(expected)}")
    print(f"Actual:   {sorted(actual)}")
    
    assert actual == expected, f"Test case 4 failed!\nExpected: {sorted(expected)}\nActual: {sorted(actual)}\nMissing: {sorted(expected - actual)}\nExtra: {sorted(actual - expected)}"

def test_case_5():
    """Test case 5: ek = Eikosany(master_set='asterisk'), pattern = [11,6,10,15,18,8]"""
    print("\nTesting case 5...")
    ek = Eikosany(master_set='asterisk')
    result = match_pattern(ek, [11, 6, 10, 15, 18, 8])
    
    expected = {
        (0, 1, 4, 5, 10, 15), (0, 2, 4, 7, 15, 18), (0, 4, 7, 9, 12, 16), 
        (0, 6, 10, 12, 14, 15), (1, 3, 6, 10, 11, 13), (2, 3, 7, 9, 13, 19), 
        (4, 5, 7, 9, 17, 19), (6, 11, 13, 14, 17, 19), (8, 9, 11, 13, 16, 19)
    }
    actual = {tuple(sorted(match)) for match in result}
    
    print(f"Expected: {sorted(expected)}")
    print(f"Actual:   {sorted(actual)}")
    
    assert actual == expected, f"Test case 5 failed!\nExpected: {sorted(expected)}\nActual: {sorted(actual)}\nMissing: {sorted(expected - actual)}\nExtra: {sorted(actual - expected)}"

def test_case_6():
    """Test case 6: ek = Eikosany(master_set='asterisk'), pattern = [11,6,10,14]"""
    print("\nTesting case 6...")
    ek = Eikosany(master_set='asterisk')
    result = match_pattern(ek, [11, 6, 10, 14])
    
    expected = {
        (0, 4, 5, 7), (0, 4, 12, 15), (0, 10, 15, 18), (1, 6, 10, 15), 
        (2, 4, 7, 9), (3, 11, 13, 19), (6, 8, 11, 13), (7, 9, 16, 19), 
        (9, 13, 17, 19)
    }
    actual = {tuple(sorted(match)) for match in result}
    
    print(f"Expected: {sorted(expected)}")
    print(f"Actual:   {sorted(actual)}")
    
    assert actual == expected, f"Test case 6 failed!\nExpected: {sorted(expected)}\nActual: {sorted(actual)}\nMissing: {sorted(expected - actual)}\nExtra: {sorted(actual - expected)}"

def test_case_7():
    """Test case 7: ek = Eikosany(master_set='asterisk'), pattern = [6,14,17,12]"""
    print("\nTesting case 7...")
    ek = Eikosany(master_set='asterisk')
    result = match_pattern(ek, [6, 14, 17, 12])
    
    # Convert expected tuples to sorted tuples (order-independent)
    expected_raw = [
        (10, 1, 3, 5), (15, 18, 8, 2), (0, 12, 14, 16), (4, 5, 17, 1), 
        (7, 2, 3, 18), (9, 16, 8, 12), (19, 17, 14, 5), (13, 3, 2, 1), 
        (11, 8, 16, 18)
    ]
    expected = {tuple(sorted(exp)) for exp in expected_raw}
    actual = {tuple(sorted(match)) for match in result}
    
    print(f"Expected: {sorted(expected)}")
    print(f"Actual:   {sorted(actual)}")
    
    assert actual == expected, f"Test case 7 failed!\nExpected: {sorted(expected)}\nActual: {sorted(actual)}\nMissing: {sorted(expected - actual)}\nExtra: {sorted(actual - expected)}"

def test_case_8():
    """Test case 8: ek = Eikosany(master_set='asterisk'), pattern = [11,6,10,8,1]"""
    print("\nTesting case 8...")
    ek = Eikosany(master_set='asterisk')
    result = match_pattern(ek, [11, 6, 10, 8, 1])
    
    # Convert expected tuples to sorted tuples (order-independent)
    expected_raw = [
        (6, 10, 15, 14, 18), (10, 15, 0, 12, 1), (0, 15, 4, 5, 18), 
        (4, 0, 7, 2, 12), (7, 4, 9, 16, 5), (9, 7, 19, 17, 2), 
        (19, 9, 13, 3, 16), (13, 19, 11, 8, 17), (11, 13, 6, 3, 14)
    ]
    expected = {tuple(sorted(exp)) for exp in expected_raw}
    actual = {tuple(sorted(match)) for match in result}
    
    print(f"Expected: {sorted(expected)}")
    print(f"Actual:   {sorted(actual)}")
    
    assert actual == expected, f"Test case 8 failed!\nExpected: {sorted(expected)}\nActual: {sorted(actual)}\nMissing: {sorted(expected - actual)}\nExtra: {sorted(actual - expected)}"

def main():
    print("Running match_pattern tests...\n")
    
    try:
        test_case_1()
        test_case_2()
        test_case_3()
        test_case_4()
        test_case_5()
        test_case_6()
        test_case_7()
        test_case_8()
        print("\n🎉 All tests passed!")
        return 0
    except AssertionError as e:
        print(f"\n💥 Test failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
