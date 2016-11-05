import sys
import re
from importlib import import_module
import traceback
import platform
import copy

class color:
    COLOR_PLATFORMS = ['Darwin', 'Linux']
    if platform.system() in COLOR_PLATFORMS:
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARN = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
    else:
        OKBLUE, OKGREEN, WARN, FAIL, ENDC = '', '', '', '', ''

def anyjoin(lst):
    """ Join the items of lst into a string with each item's __repr__ """
    return ", ".join(map(repr, lst))

class TestCase:
    def __init__(self, ins=None, out=None):
        self.inputs = ins
        self.output = out
    def run(self, function_ref):
        try:
            result = function_ref(*self.inputs)
        except Exception as e:
            return False, self.format_error_message(traceback.format_exc())
        if result == self.output:
            return True, self.format_success_message()
        else:
            return False, self.format_error_message(result)
    def format_success_message(self):
        return color.OKGREEN + "Passed. " + color.ENDC + "With inputs %s, returned %s." \
                % (anyjoin(self.inputs), self.output)
    def format_error_message(self, got):
        return color.FAIL + "Failed. " + color.ENDC + "With inputs %s, expected %s, instead got:\n %s" \
                % (anyjoin(self.inputs), self.output, got)

class MutableTestCase:
    def __init__(self, ins=None, outs=None, mutable_indices=0):
        if not (isinstance(ins, tuple) and isinstance(outs, tuple)):
            raise ValueError("Inputs and outputs must be listed in tuples.")
        self.inputs = ins
        self.outputs = outs
        if hasattr(mutable_indices, "__iter__"):
            self.mutable_indices = mutable_indices
        else:
            self.mutable_indices = [mutable_indices]
        self.frozen_inputs = anyjoin(self.inputs)
    def run(self, function_ref):
        try:
            mutable_inputs = [self.inputs[i] for i in self.mutable_indices]
            function_ref(*self.inputs)
            passed = tuple(mutable_inputs) == self.outputs
        except Exception as e:
            return False, self.format_error_message(traceback.format_exc())
        if passed:
            return True, self.format_success_message()
        else:
            return False, self.format_error_message(anyjoin(mutable_inputs))
    def format_success_message(self):
        return color.OKGREEN + "Passed. " + color.ENDC + "With inputs: %s; input(s) # %s became %s." \
                % (self.frozen_inputs, anyjoin(self.mutable_indices), anyjoin(self.outputs))
    def format_error_message(self, got):
        return color.FAIL + "Failed. " + color.ENDC + "With inputs: %s; expected input(s) # %s to become %s; instead got:\n %s" \
                % (self.frozen_inputs, anyjoin(self.mutable_indices), anyjoin(self.outputs), got)

class Exercise:
    def __init__(self, name, module, func_name):
        self.module = module
        self.func_name = func_name
        self.name = name
        self.tests = []
    def add_test(self, test_case):
        self.tests.append(test_case)
    def run_tests(self):
        print("Running tests for %s\n=============" % self.name)
        try:
            func = getattr(self.module, self.func_name)
        except AttributeError:
            print(color.WARN + "Fail: " + color.ENDC + "no function named '%s' exists\n" % self.func_name)
            return
        results = []
        for i in range(len(self.tests)):
            result, message = self.do_test(i, func)
            print(message)
            results.append(result)
        success_rate = sum(results)/len(results)
        if success_rate == 1:
            print("You passed all of the tests!\n")
        else:
            print("You passed %s/%s tests.\n" % (sum(results), len(results)))
    def do_test(self, test_index, function_ref):
        result, message = self.tests[test_index].run(function_ref)
        return result, message

def import_file_or_fail(filename):
    modulename = re.sub(r"\.py$", "", filename)
    try:
        return __import__(modulename, globals(), locals(), ['*'])
    except ImportError:
        print("Error: could not find file %s" % filename)
        exit()

def main():
    try:
        filename = sys.argv[1]
    except IndexError:
        print("Error: please provide a file to be tested.")
        exit()
    testmodule = import_file_or_fail(filename)
    # current_module = sys.modules[__name__]

    exercise_1 = Exercise("exercise 1: Push First Odd Back", testmodule, "push_first_odd_back")
    exercise_1.add_test(MutableTestCase(ins=([2, 3, 4, 5],), outs=([2, 4, 5, 3],)))
    exercise_1.add_test(MutableTestCase(ins=([2, 4, 6, 8],), outs=([2, 4, 6, 8],)))
    exercise_1.add_test(MutableTestCase(ins=([0, 0, 1],), outs=([0, 0, 1],)))
    exercise_1.run_tests()

    exercise_2 = Exercise("exercise 2: Flatten", testmodule, "flatten")
    exercise_2.add_test(TestCase(ins=([["a", "b"],["c", "d", "e"], ["f"]],), out=["a", "b", "c", "d", "e", "f"]))
    exercise_2.run_tests()

    exercise_3_1 = Exercise("exercise 3.1: Squares of Evens", testmodule, "squares_of_evens")
    exercise_3_1.add_test(TestCase(ins=([-5, -2, 0, 1, 3, 4, 8],), out=[4, 0, 16, 64]))
    exercise_3_1.run_tests()

    exercise_3_2 = Exercise("exercise 3.2: Nth Power of Evens", testmodule, "nth_power_of_evens")
    exercise_3_2.add_test(TestCase(ins=([-5, -2, 0, 1, 3, 4, 8], 3), out=[-8, 0, 32, 128]))
    exercise_3_2.run_tests()

    exercise_4 = Exercise("exercise 4: Substitute Base", testmodule, "substitute_base")
    exercise_4.add_test(TestCase(ins=("AAGTTAGTCA", "A", "C"), out="CCGTTCGTCG"))
    exercise_4.run_tests()

    exercise_5 = Exercise("exercise 5: Combine", testmodule, "combine")
    exercise_5.add_test(TestCase(ins=([1, 2, 3, 4, 5],), out=15))
    exercise_5.add_test(TestCase(ins=(["hello ", "my ", "name ", "is ", "someone?"],), out="hello my name is someone?"))
    exercise_5.run_tests()

    exercise_6 = Exercise("exercise 6: Base Frequency", testmodule, "base_freq")
    exercise_6.add_test(TestCase(ins=("AAGTTAGTCA",), out={"A": 4, "C": 1, "G": 2, "T": 3}))
    exercise_6.run_tests()

    exercise_7_1 = Exercise("exercise 7.1: Substitute Characters", testmodule, "substitute_chars")
    replacements = {"S":"Z", "E":"U", "T":"P", "A":"M"}
    exercise_7_1.add_test(TestCase(ins=("SECRET MESSAGE", replacements), out="ZUCRUP MUZZMGE"))
    exercise_7_1.run_tests()

    exercise_7_2 = Exercise("exercise 7.2: Invert Dictionary", testmodule, "invert_dict")
    exercise_7_2.add_test(TestCase(ints=({"A":"X", "B":"Y", "C":"Z"},), out={"X":"A", "Z":"C", "Y":"B"}))
    exercise_7_2.run_tests()

if __name__ == "__main__":
    main()
