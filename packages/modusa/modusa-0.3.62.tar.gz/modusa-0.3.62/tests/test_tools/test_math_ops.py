#!/usr/bin/env python3


#--------Meta Information----------
_class_name = "MathOps"
_author_name = "Ankit Anand"
_author_email = "ankit0.anand0@gmail.com"
_created_at = "2025-07-12"
#----------------------------------

from modusa import excp
from modusa.tools.math_ops import MathOps
import pytest
import numpy as np

#-------------------
# add method
#-------------------
@pytest.mark.parametrize("a, b", [
	(None, 10),
	(10, None),
	(None, None),
	("10", 10),
	(11, "10"),
	("11", "10")
])
def test_add_invalid_inputs(a, b):
	with pytest.raises(excp.InputError):
		MathOps.add(a, b)
		
@pytest.mark.parametrize("a, b, expected", [
	(10, 10, 20),
	(np.array([1, 2, 3]), 10, np.array([11, 12, 13])),
	([10, 20], 10, np.array([20, 30])),
	([10, 20], np.array(10), np.array([20, 30])),
	([10, 20], [10], np.array([20, 30])),
	(np.array([10, 20]), np.array(10), np.array([20, 30]))
])
def test_add_valid_inputs(a, b, expected):
	result = MathOps.add(a, b)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, expected)

@pytest.mark.parametrize("a, b", [
	(np.array([10, 20]), np.array([10, 20, 30])),
	([10, 20], [10, 20, 30])
])
def test_add_incompatible_shapes(a, b):
	with pytest.raises(excp.InputError):
		MathOps.add(a, b)
		
#-------------------
# subtract method
#-------------------
@pytest.mark.parametrize("a, b", [
	(None, 10),
	(10, None),
	(None, None),
	("10", 10),
	(11, "10"),
	("11", "10")
])
def test_subtract_invalid_inputs(a, b):
	with pytest.raises(excp.InputError):
		MathOps.subtract(a, b)
		
@pytest.mark.parametrize("a, b, expected", [
	(10, 10, 0),
	(np.array([1, 2, 3]), 10, np.array([-9, -8, -7])),
	([10, 20], 10, np.array([0, 10])),
	([10, 20], np.array(10), np.array([0, 10])),
	([10, 20], [10], np.array([0, 10])),
	(np.array([10, 20]), np.array(10), np.array([0, 10]))
])
def test_subtract_valid_inputs(a, b, expected):
	result = MathOps.subtract(a, b)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, expected)
	
@pytest.mark.parametrize("a, b", [
	(np.array([10, 20]), np.array([10, 20, 30])),
	([10, 20], [10, 20, 30])
])
def test_subtract_incompatible_shapes(a, b):
	with pytest.raises(excp.InputError):
		MathOps.subtract(a, b)
		
#-------------------
# multiply method
#-------------------
@pytest.mark.parametrize("a, b", [
	(None, 10),
	(10, None),
	(None, None),
	("10", 10),
	(11, "10"),
	("11", "10")
])
def test_multiply_invalid_inputs(a, b):
	with pytest.raises(excp.InputError):
		MathOps.multiply(a, b)
		
@pytest.mark.parametrize("a, b, expected", [
	(10, 10, 100),
	(np.array([1, 2, 3]), 10, np.array([10, 20, 30])),
	([10, 20], 10, np.array([100, 200])),
	([10, 20], np.array(10), np.array([100, 200])),
	([10, 20], [10], np.array([100, 200])),
	(np.array([10, 20]), np.array(10), np.array([100, 200]))
])
def test_multiply_valid_inputs(a, b, expected):
	result = MathOps.multiply(a, b)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, expected)
	
@pytest.mark.parametrize("a, b", [
	(np.array([10, 20]), np.array([10, 20, 30])),
	([10, 20], [10, 20, 30])
])
def test_multiply_incompatible_shapes(a, b):
	with pytest.raises(excp.InputError):
		MathOps.multiply(a, b)
		

#-------------------
# division method
#-------------------
@pytest.mark.parametrize("a, b", [
	(None, 10),
	(10, None),
	(None, None),
	("10", 10),
	(11, "10"),
	("11", "10"),
])
def test_divide_invalid_inputs(a, b):
	with pytest.raises(excp.InputError):
		MathOps.divide(a, b)
		
@pytest.mark.parametrize("a, b, expected", [
	(10, 10, 1.0),
	(np.array([1, 2, 3]), 10, np.array([0.1, 0.2, 0.3])),
	([10, 20], 10, np.array([1, 2])),
	([10, 20], np.array(10), np.array([1, 2])),
	([10, 20], [10], np.array([1, 2])),
	(np.array([10, 20]), np.array(10), np.array([1, 2]))
])
def test_divide_valid_inputs(a, b, expected):
	result = MathOps.divide(a, b)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, expected)
	
@pytest.mark.parametrize("a, b", [
	(np.array([10, 20]), np.array([10, 20, 30])),
	([10, 20], [10, 20, 30])
])
def test_divide_incompatible_shapes(a, b):
	with pytest.raises(excp.InputError):
		MathOps.divide(a, b)
		
#-------------------
# power method
#-------------------
@pytest.mark.parametrize("a, b", [
	(None, 10),
	(10, None),
	(None, None),
	("10", 10),
	(11, "10"),
	("11", "10"),
])
def test_power_invalid_inputs(a, b):
	with pytest.raises(excp.InputError):
		MathOps.power(a, b)
		
@pytest.mark.parametrize("a, b, expected", [
	(10, 2, 100),
	(np.array([1, 2, 3]), 2, np.array([1, 4, 9])),
	([10, 20], 2, np.array([100, 400])),
	([10, 20], np.array(2), np.array([100, 400])),
	([10, 20], [2], np.array([100, 400])),
	(np.array([10, 20]), np.array(2), np.array([100, 400]))
])
def test_power_valid_inputs(a, b, expected):
	result = MathOps.power(a, b)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, expected)
	
@pytest.mark.parametrize("a, b", [
	(np.array([10, 20]), np.array([10, 20, 30])),
	([10, 20], [10, 20, 30])
])
def test_power_incompatible_shapes(a, b):
	with pytest.raises(excp.InputError):
		MathOps.power(a, b)
		
#----------------------
# floor divide method
#----------------------
@pytest.mark.parametrize("a, b", [
	(None, 10),
	(10, None),
	(None, None),
	("10", 10),
	(11, "10"),
	("11", "10"),
])
def test_floor_divide_invalid_inputs(a, b):
	with pytest.raises(excp.InputError):
		MathOps.floor_divide(a, b)
		
@pytest.mark.parametrize("a, b, expected", [
	(10, 2, 5),
	(np.array([1, 2, 3]), 2, np.array([0, 1, 1])),
	([10, 20], 3, np.array([3, 6])),
	([10, 20], np.array(4), np.array([2, 5])),
	([10, 20], [5], np.array([2, 4])),
	(np.array([10, 20]), np.array(2), np.array([5, 10]))
])
def test_floor_divide_valid_inputs(a, b, expected):
	result = MathOps.floor_divide(a, b)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, expected)
	
@pytest.mark.parametrize("a, b", [
	(np.array([10, 20]), np.array([10, 20, 30])),
	([10, 20], [10, 20, 30])
])
def test_floor_divide_incompatible_shapes(a, b):
	with pytest.raises(excp.InputError):
		MathOps.floor_divide(a, b)
		
#-------------------
# mean method
#-------------------
@pytest.mark.parametrize("a", [
	(None),
	("10"),
])
def test_mean_invalid_inputs(a):
	with pytest.raises(excp.InputError):
		MathOps.mean(a)
		
@pytest.mark.parametrize("a, expected", [
	(10, 10),
	(np.array([1, 2, 3]), 2),
	([10, 20], 15),
	(np.array([10, 20]), 15)
])
def test_mean_valid_inputs(a, expected):
	result = MathOps.mean(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, expected)
	
@pytest.mark.parametrize("a, axis, expected", [
	(np.array([[10, 20], [10, 20], [10, 20]]), 0, np.array([10, 20])),
	(np.array([[10, 20], [10, 30], [10, 20]]), 1, np.array([15, 20, 15])),
])
def test_mean_along_an_axis(a, axis, expected):
	result = MathOps.mean(a, axis=axis)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, expected)
	

#-------------------
# std method
#-------------------
@pytest.mark.parametrize("a", [
	(None),
	("10"),
])
def test_std_invalid_inputs(a):
	with pytest.raises(excp.InputError):
		MathOps.std(a)
		
@pytest.mark.parametrize("a, expected", [
	(10, 0),
	(np.array([10, 11]), 0.5),
	([10, 20], 5),
	(np.array([10, 20]), 5)
])
def test_std_valid_inputs(a, expected):
	result = MathOps.std(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, expected)
	
@pytest.mark.parametrize("a, axis, expected", [
	(np.array([[10, 20], [11, 20], [12, 20]]), 0, np.array([0.81649658, 0.0])),
	(np.array([[10, 20], [11, 20], [12, 20]]), 1, np.array([5., 4.5, 4.])),
])
def test_std_along_an_axis(a, axis, expected):
	result = MathOps.std(a, axis=axis)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, expected)
	
#-------------------
# min method
#-------------------
@pytest.mark.parametrize("a", [
	("10"),
])
def test_min_invalid_inputs(a):
	with pytest.raises(excp.InputError):
		MathOps.min(a)
		
@pytest.mark.parametrize("a, expected", [
	(10, 10),
	(np.array([10, 11]), 10),
	([10, 20], 10),
	(np.array([11, 20]), 11)
])
def test_min_valid_inputs(a, expected):
	result = MathOps.min(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, expected)
	
@pytest.mark.parametrize("a, axis, expected", [
	(np.array([[10, 20], [11, 20], [12, 20]]), 0, np.array([10, 20])),
	(np.array([[10, 20], [11, 21], [12, 22]]), 1, np.array([10, 11, 12])),
])
def test_min_along_an_axis(a, axis, expected):
	result = MathOps.min(a, axis=axis)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, expected)
	
#-------------------
# max method
#-------------------
@pytest.mark.parametrize("a", [
	("10"),
])
def test_max_invalid_inputs(a):
	with pytest.raises(excp.InputError):
		MathOps.max(a)
		
@pytest.mark.parametrize("a, expected", [
	(10, 10),
	(np.array([10, 11]), 11),
	([10, 20], 20),
	(np.array([11, 20]), 20)
])
def test_max_valid_inputs(a, expected):
	result = MathOps.max(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, expected)
	
@pytest.mark.parametrize("a, axis, expected", [
	(np.array([[10, 20], [11, 20], [12, 20]]), 0, np.array([12, 20])),
	(np.array([[10, 20], [11, 21], [12, 22]]), 1, np.array([20, 21, 22])),
])
def test_max_along_an_axis(a, axis, expected):
	result = MathOps.max(a, axis=axis)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, expected)
	
#-------------------
# sum method
#-------------------
@pytest.mark.parametrize("a", [
	("10"),
])
def test_sum_invalid_inputs(a):
	with pytest.raises(excp.InputError):
		MathOps.sum(a)
		
@pytest.mark.parametrize("a, expected", [
	(10, 10),
	(np.array([10, 11]), 21),
	([10, 20], 30),
	(np.array([11, 20]), 31)
])
def test_sum_valid_inputs(a, expected):
	result = MathOps.sum(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, expected)
	
@pytest.mark.parametrize("a, axis, expected", [
	(np.array([[10, 20], [11, 20], [12, 20]]), 0, np.array([33, 60])),
	(np.array([[10, 20], [11, 21], [12, 22]]), 1, np.array([30, 32, 34])),
])
def test_sum_along_an_axis(a, axis, expected):
	result = MathOps.sum(a, axis=axis)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, expected)
	
#-------------------
# sin method
#-------------------
@pytest.mark.parametrize("a", [
	("10"),
])
def test_sin_invalid_inputs(a):
	with pytest.raises(excp.InputError):
		MathOps.sin(a)
		
@pytest.mark.parametrize("a", [
	10,
	np.array([10, 11]),
	[10, 20],
	np.array([11, 20])
])
def test_sin_valid_inputs(a):
	result = MathOps.sin(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, np.sin(a))
	
@pytest.mark.parametrize("a", [
	(np.array([[10, 20], [11, 20], [12, 20]])),
	(np.array([[10, 20], [11, 21], [12, 22]])),
])
def test_sin_along_an_axis(a):
	result = MathOps.sin(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, np.sin(a))
	

#-------------------
# cos method
#-------------------
@pytest.mark.parametrize("a", [
	("10"),
])
def test_cos_invalid_inputs(a):
	with pytest.raises(excp.InputError):
		MathOps.cos(a)
		
@pytest.mark.parametrize("a", [
	10,
	np.array([10, 11]),
	[10, 20],
	np.array([11, 20])
])
def test_cos_valid_inputs(a):
	result = MathOps.cos(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, np.cos(a))
	
@pytest.mark.parametrize("a", [
	(np.array([[10, 20], [11, 20], [12, 20]])),
	(np.array([[10, 20], [11, 21], [12, 22]])),
])
def test_cos_along_an_axis(a):
	result = MathOps.cos(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, np.cos(a))
	
#-------------------
# tanh method
#-------------------
@pytest.mark.parametrize("a", [
	("10"),
])
def test_tanh_invalid_inputs(a):
	with pytest.raises(excp.InputError):
		MathOps.tanh(a)
		
@pytest.mark.parametrize("a", [
	10,
	np.array([10, 11]),
	[10, 20],
	np.array([11, 20])
])
def test_tanh_valid_inputs(a):
	result = MathOps.tanh(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, np.tanh(a))
	
@pytest.mark.parametrize("a", [
	(np.array([[10, 20], [11, 20], [12, 20]])),
	(np.array([[10, 20], [11, 21], [12, 22]])),
])
def test_tanh_along_an_axis(a):
	result = MathOps.tanh(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, np.tanh(a))
	
#-------------------
# exp method
#-------------------
@pytest.mark.parametrize("a", [
	("10"),
])
def test_exp_invalid_inputs(a):
	with pytest.raises(excp.InputError):
		MathOps.exp(a)
		
@pytest.mark.parametrize("a", [
	10,
	np.array([10, 11]),
	[10, 20],
	np.array([11, 20])
])
def test_exp_valid_inputs(a):
	result = MathOps.exp(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, np.exp(a))
	
@pytest.mark.parametrize("a", [
	(np.array([[10, 20], [11, 20], [12, 20]])),
	(np.array([[10, 20], [11, 21], [12, 22]])),
])
def test_exp_along_an_axis(a):
	result = MathOps.exp(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, np.exp(a))
	
#-------------------
# log method
#-------------------
@pytest.mark.parametrize("a", [
	("10"),
])
def test_log_invalid_inputs(a):
	with pytest.raises(excp.InputError):
		MathOps.log(a)
		
@pytest.mark.parametrize("a", [
	10,
	np.array([10, 11]),
	[10, 20],
	np.array([11, 20])
])
def test_log_valid_inputs(a):
	result = MathOps.log(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, np.log(a))
	
@pytest.mark.parametrize("a", [
	(np.array([[10, 20], [11, 20], [12, 20]])),
	(np.array([[10, 20], [11, 21], [12, 22]])),
])
def test_log_along_an_axis(a):
	result = MathOps.log(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, np.log(a))
	
#-------------------
# log10 method
#-------------------
@pytest.mark.parametrize("a", [
	("10"),
])
def test_log10_invalid_inputs(a):
	with pytest.raises(excp.InputError):
		MathOps.log10(a)
		
@pytest.mark.parametrize("a", [
	10,
	np.array([10, 11]),
	[10, 20],
	np.array([11, 20])
])
def test_log10_valid_inputs(a):
	result = MathOps.log10(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, np.log10(a))
	
@pytest.mark.parametrize("a", [
	(np.array([[10, 20], [11, 20], [12, 20]])),
	(np.array([[10, 20], [11, 21], [12, 22]])),
])
def test_log10_along_an_axis(a):
	result = MathOps.log10(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, np.log10(a))
	
#-------------------
# log2 method
#-------------------
@pytest.mark.parametrize("a", [
	("10"),
])
def test_log2_invalid_inputs(a):
	with pytest.raises(excp.InputError):
		MathOps.log2(a)
		
@pytest.mark.parametrize("a", [
	10,
	np.array([10, 11]),
	[10, 20],
	np.array([11, 20])
])
def test_log2_valid_inputs(a):
	result = MathOps.log2(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, np.log2(a))
	
@pytest.mark.parametrize("a", [
	(np.array([[10, 20], [11, 20], [12, 20]])),
	(np.array([[10, 20], [11, 21], [12, 22]])),
])
def test_log2_along_an_axis(a):
	result = MathOps.log2(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, np.log2(a))
	
#-------------------
# log1p method
#-------------------
@pytest.mark.parametrize("a", [
	("10"),
])
def test_log1p_invalid_inputs(a):
	with pytest.raises(excp.InputError):
		MathOps.log1p(a)
		
@pytest.mark.parametrize("a", [
	10,
	np.array([10, 11]),
	[10, 20],
	np.array([11, 20])
])
def test_log1p_valid_inputs(a):
	result = MathOps.log1p(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, np.log1p(a))
	
@pytest.mark.parametrize("a", [
	(np.array([[10, 20], [11, 20], [12, 20]])),
	(np.array([[10, 20], [11, 21], [12, 22]])),
])
def test_log1p_along_an_axis(a):
	result = MathOps.log1p(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, np.log1p(a))
	
#-------------------
# sqrt method
#-------------------
@pytest.mark.parametrize("a", [
	("10"),
])
def test_sqrt_invalid_inputs(a):
	with pytest.raises(excp.InputError):
		MathOps.sqrt(a)
		
@pytest.mark.parametrize("a", [
	10,
	np.array([10, 11]),
	[10, 20],
	np.array([11, 20])
])
def test_sqrt_valid_inputs(a):
	result = MathOps.sqrt(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, np.sqrt(a))
	
@pytest.mark.parametrize("a", [
	(np.array([[10, 20], [11, 20], [12, 20]])),
	(np.array([[10, 20], [11, 21], [12, 22]])),
])
def test_sqrt_along_an_axis(a):
	result = MathOps.sqrt(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, np.sqrt(a))
	
#-------------------
# abs method
#-------------------
@pytest.mark.parametrize("a", [
	("10"),
])
def test_abs_invalid_inputs(a):
	with pytest.raises(excp.InputError):
		MathOps.sqrt(a)
		
@pytest.mark.parametrize("a", [
	-10,
	np.array([10, 11]),
	[10, 20],
	np.array([11, -20])
])
def testabst_valid_inputs(a):
	result = MathOps.abs(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, np.abs(a))
	
@pytest.mark.parametrize("a", [
	(np.array([[10, 20], [11, -20], [-12, 20]])),
	(np.array([[10, -20], [11, 21], [-12, 22]])),
])
def test_abs_along_an_axis(a):
	result = MathOps.abs(a)
	assert isinstance(result, (np.ndarray, np.generic))
	assert np.allclose(result, np.abs(a))
	
	