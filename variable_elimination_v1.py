class Variable(object):
    def __init__(self, string):
        if '~' in string:
            self.is_false = True
            self.symbol = string[1:]
        else:
            self.is_false = False
            self.symbol = string

    def __eq__(self, other):
        return self.is_false == other.is_false and self.symbol == other.symbol

    def __repr__(self):
        if not self.is_false:
            return self.symbol
        return "~" + self.symbol

    def __hash__(self):
        return hash(str(self.symbol))


class VariableList(object):
    def __init__(self, symbols, var_list=None, entry=None):
        if var_list:
            self.variables = list(var_list)
        elif entry:
            self.variables = list(entry.variables)
        else:
            self.variables = [Variable(var) for var in symbols]

    def __eq__(self, other):
        return self.variables == other.variables

    def __repr__(self):
        return str(self.variables)

    def __iter__(self):
        return iter(self.variables)

    def __hash__(self):
        return hash(tuple(self.variables))


class Factor(object):
    def __init__(self, copy_factor=None):
        if copy_factor:
            self.entries = dict(copy_factor.entries)
        else:
            self.entries = {}

    def __iter__(self):
        return iter(self.entries)

    def __eq__(self, other):
        return list(self.entries.keys()) == list(other.entries.keys())

    def __repr__(self):
        result = ""
        for key in self.entries:
            result += str(key) + " = " + str(self.entries[key]) + '\n'
        return result

    def include(self, var):
        for param in list(self.entries.keys()):
            if var in param.variables:
                return True
        return False

    def is_empty(self):
        for param in list(self.entries.keys()):
            if param.variables:
                return False
        return True


def restrict(factor, variable):
    var_list = list(factor.entries.keys())[0]
    result = Factor()
    # Symbol not found, simply return
    if variable.symbol not in [x.symbol for x in var_list.variables]:
        return factor
    for entry in factor.entries:
        if variable in entry.variables:
            new_vars = VariableList("", None, entry)
            new_vars.variables.remove(variable)
            result.entries[new_vars] = factor.entries[entry]
    return result


def multiply(factor1, factor2):
    factor1_vars = factor1.entries.keys()[0]
    factor2_vars = factor2.entries.keys()[0]
    factor1_syms = [x.symbol for x in factor1_vars]
    factor2_syms = [x.symbol for x in factor2_vars]
    common_syms = set(factor1_syms).intersection(set(factor2_syms))
    result = Factor()
    for f1_entry in factor1.entries:
        for f2_entry in factor2.entries:
            # Identify intersection, form new var_list with union, multiply to get result
            var_intersection = set(x for x in f1_entry.variables).intersection(
                set(x for x in f2_entry.variables))
            if len(var_intersection) == len(common_syms):
                new_var_list = list(set(x for x in f1_entry.variables).union(
                    set(x for x in f2_entry.variables)))
                result.entries[VariableList("", new_var_list, None)] = \
                    factor1.entries[f1_entry] * factor2.entries[f2_entry]
    return result


def sumout(factor, variable):
    not_var = Variable(str(variable))
    not_var.is_false = not variable.is_false
    result = Factor()
    for entry in factor.entries:
        reduced_entries = None
        if not_var in entry.variables or variable in entry.variables:
            reduced_entries = VariableList("", None, entry)
            if not_var in entry.variables:
                reduced_entries.variables.remove(not_var)
            else:
                reduced_entries.variables.remove(variable)
        if reduced_entries in result.entries.keys():
            result.entries[reduced_entries] += factor.entries[entry]
        else:
            result.entries[reduced_entries] = factor.entries[entry]
    return result


def normalize(factor):
    result = Factor(factor)
    total = sum(result.entries.values())
    for key in result.entries:
        result.entries[key] /= total
    return result


def print_factors(factorlist):
    result = ""
    for x in range(len(factorlist)):
        if not factorlist[x].is_empty():
            result += str(factorlist[x]) + '\n'
    print result


def inference(factor_list, query_vars, ol_hidden_vars, evidence_list):
    print "Query:", query_vars
    print "Hidden Vars:", ol_hidden_vars
    print "Evidence List:", evidence_list
    print "Initial Factors: "
    print_factors(factor_list)

    print "-------------STAGE 1: RESTRICT---------------"
    for x in range(len(factor_list)):
        for label in evidence_list:
            r = restrict(factor_list[x], label)
            factor_list[x] = r

    print "Restricted Factors: "
    print_factors(factor_list)
    print "-------------STAGE 2: MULTPLY---------------"
    for var in ol_hidden_vars:
        print "Hidden Variable:", var
        filtered_factors = [Factor(factor) for factor in factor_list if factor.include(var)]
        print "Factors being multiplied:"
        print_factors(filtered_factors)
        product = filtered_factors[0]
        for x in filtered_factors[1:]:
            product = multiply(product, x)
        print "Product:", '\n', product

        print "Summing out: ", var
        result = sumout(product, var)
        print "Result after sumout: ", '\n', result
        factor_list = [Factor(factor) for factor in factor_list if not factor.include(var)]
        factor_list.append(result)

    result = factor_list[0]
    for factor in factor_list[1:]:
        result = multiply(result, factor)

    print "Result before normalization: ", '\n', result

    print "-------------STAGE 3: NORMALIZATION---------------"
    final = normalize(result)
    print "Result after normalization: ", '\n', final

    print "---------------------DONE-------------------------"
    return final.entries[VariableList("", query_vars, None)]


def get_fp():
    factor = Factor()
    factor.entries[VariableList(["FP", "FRAUD", "TRAV"])] = 0.9
    factor.entries[VariableList(["FP", "FRAUD", "~TRAV"])] = 0.1
    factor.entries[VariableList(["FP", "~FRAUD", "TRAV"])] = 0.9
    factor.entries[VariableList(["FP", "~FRAUD", "~TRAV"])] = 0.01
    factor.entries[VariableList(["~FP", "FRAUD", "TRAV"])] = 0.1
    factor.entries[VariableList(["~FP", "FRAUD", "~TRAV"])] = 0.9
    factor.entries[VariableList(["~FP", "~FRAUD", "TRAV"])] = 0.1
    factor.entries[VariableList(["~FP", "~FRAUD", "~TRAV"])] = 0.99
    return factor


def get_ip():
    factor = Factor()
    factor.entries[VariableList(["IP", "FRAUD", "OC"])] = 0.15
    factor.entries[VariableList(["IP", "FRAUD", "~OC"])] = 0.051
    factor.entries[VariableList(["IP", "~FRAUD", "OC"])] = 0.1
    factor.entries[VariableList(["IP", "~FRAUD", "~OC"])] = 0.001
    factor.entries[VariableList(["~IP", "FRAUD", "OC"])] = 0.85
    factor.entries[VariableList(["~IP", "FRAUD", "~OC"])] = 0.949
    factor.entries[VariableList(["~IP", "~FRAUD", "OC"])] = 0.9
    factor.entries[VariableList(["~IP", "~FRAUD", "~OC"])] = 0.999
    return factor


def get_crp():
    factor = Factor()
    factor.entries[VariableList(["CRP", "OC"])] = 0.1
    factor.entries[VariableList(["CRP", "~OC"])] = 0.01
    factor.entries[VariableList(["~CRP", "OC"])] = 0.9
    factor.entries[VariableList(["~CRP", "~OC"])] = 0.99
    return factor


def get_fraud():
    factor = Factor()
    factor.entries[VariableList(["FRAUD", "TRAV"])] = 0.01
    factor.entries[VariableList(["FRAUD", "~TRAV"])] = 0.004
    factor.entries[VariableList(["~FRAUD", "TRAV"])] = 0.99
    factor.entries[VariableList(["~FRAUD", "~TRAV"])] = 0.996
    return factor


def get_trav():
    factor = Factor()
    factor.entries[VariableList(["TRAV"])] = 0.05
    factor.entries[VariableList(["~TRAV"])] = 0.95
    return factor


def get_oc():
    factor = Factor()
    factor.entries[VariableList(["OC"])] = 0.8
    factor.entries[VariableList(["~OC"])] = 0.2
    return factor


def main():
    # Query can be specified by modifying the following section
    trav = get_trav()
    fp = get_fp()
    fraud = get_fraud()
    ip = get_ip()
    oc = get_oc()
    crp = get_crp()

    factors = [trav, fp, fraud, ip, oc, crp]

    query = [Variable("FRAUD")]
    hidden = []
    evidence = [Variable("IP"), Variable("~FP"), Variable("~TRAV"), Variable("CRP"), Variable("OC")]
    inf = inference(factors, query, hidden, evidence)
    print "Query:", query
    print "Evidence:", evidence
    print "Final Probability:", inf, "=", inf * 100, "%"

main()

