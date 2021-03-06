from EchoingSEO_reader import *
# from PlaceholderManager import *
from io import StringIO
from SEO_simulator import *


class SEO_Lista:
    """
    Whereas with Qubiter, the main way of storing circuits is **in files**,
    with programs like PyQuil (by Rigetti) and Cirq (by Google), circuits (
    aka programs) are stored **entirely in memory**, essentially as Python
    lists of gates. Lists of this type can be sliced, combined, etc. When
    using such lists, it is easy to randomly access any gate of the circuit
    at will. This is convenient, for instance, when doing circuit
    optimizations (i.e., replacing the circuit by an equivalent but
    hopefully shorter one, what IBM qiskit calls "transpiling").

    In this class, we support Qubiter's version of PyQuil's and Cirq's gate
    lists. In Qubiter, we use simply a Python list of the lines, stored as
    strings, with the ending '\n' removed, of the circuit's English file.

    Attributes
    ----------
    line_list : list[str]
    num_bits : int

    """
    def __init__(self, num_bits, line_list=None):
        """
        Constructor

        Returns
        -------

        """
        self.num_bits = num_bits
        self.line_list = line_list
        if not line_list:
            self.line_list = []

    def append(self, fun_name, param_list):
        """
        This method adds at the end of self a new single line for a single
        gate. fun_name is the name of any function in SEO_writer whose name
        starts with the string 'write_' and param_list is a list containing
        values for the arguments of fun_name. This method creates an object
        of SEO_writer called `wr` and calls

        eval('wr.' + fun_name + '(*param_list)').

        Instead of creating temporary English and Picture files as was done
        in a previous version of this function, wr now writes into
        in-streams which are StringIO that live purely in memory. This is
        much more efficient because it involves no files at any time.

        Parameters
        ----------
        num_bits : int
        fun_name : str
        param_list : list

        Returns
        -------

        """
        assert fun_name[:6] == 'write_'
        file_prefix = 'tempo970361432226978'
        emb = CktEmbedder(self.num_bits, self.num_bits)
        eng_out = StringIO()
        pic_out = StringIO()

        wr = SEO_writer(file_prefix, emb,
                        english_out=eng_out, picture_out=pic_out)

        eval('wr.' + fun_name + '(*param_list)')
        line = eng_out.getvalue().strip('\n')
        eng_out.close()
        pic_out.close()
        self.line_list.append(line)

    @staticmethod
    def eng_file_to_line_list(file_prefix, num_bits):
        """
        This static method reads an English file with file prefix
        `file_prefix` and it returns a list of its line strings. Note that
        the '\n' at the end of each line in the English file is removed
        before adding it to the line list.

        Parameters
        ----------
        file_prefix : str
        num_bits : int

        Returns
        -------
        list[str]

        """
        path = file_prefix + '_' + str(num_bits) + '_eng.txt'
        with open(path, 'r') as f:
            line_list = [line.rstrip('\n') for line in f]
        return line_list

    @staticmethod
    def line_list_to_eng_and_pic_files(line_list, file_prefix, num_bits):
        """
        This method does the reverse of eng_file_to_line_list(). It writes
        both an English file and a Picture file with file
        prefix=file_prefix. Note that an '\n' is added at the end of each
        line in the line list before writing the line to the English file.

        Parameters
        ----------
        line_list : list[str]
        file_prefix : str
        num_bits : int

        Returns
        -------
        None

        """
        end_str = '_' + str(num_bits) + '_eng.txt'
        with open(file_prefix + end_str, 'w') as f:
            for line in line_list:
                f.write(line + '\n')

        # this writes a Picture file from the English file just created
        EchoingSEO_reader.pic_file_from_eng_file(file_prefix, num_bits)

    def write_eng_and_pic_files(self, file_prefix):
        """
        This method does the same as line_list_to_eng_and_pic_files(),
        except it is called by an object of this class instead of being a
        static method.

        Parameters
        ----------
        file_prefix : str

        Returns
        -------
        None

        """
        SEO_Lista.line_list_to_eng_and_pic_files(
            self.line_list, file_prefix, self.num_bits)

    def simulate(self, init_st_vec=None, **kwargs):
        """
        This method creates temporary English and Picture file from self,
        and uses those to create an object of SEO_simulator called sim. This
        has the effect of evolving the state vector to its final state. The
        method ends by deleting the temporary files, and returning sim. The
        output sim can be used to access the final state vector, etc.

        Parameters
        ----------
        init_st_vec : StateVec
        kwargs : list
            key-word arguments of SEO_simulator

        Returns
        -------
        SEO_simulator

        """
        file_prefix = '610935122304'
        self.write_eng_and_pic_files(file_prefix)
        sim = SEO_simulator(file_prefix, self.num_bits,
                init_st_vec=init_st_vec, **kwargs)
        import os
        os.remove(ug.get_eng_file_path(file_prefix, self.num_bits))
        os.remove(ug.get_pic_file_path(file_prefix, self.num_bits))
        return sim

    def print(self):
        """
        prints self.line_list, one item per line

        Returns
        -------
        None

        """
        print('\n'.join(self.line_list))

    def get_var_nums_and_fun_names(self):
        """
        This method returns 2 lists:
        * a list of all the distinct variable numbers
        * a list of all the distinct function names
        encountered in the circuit.

        Returns
        -------
        list[int], list[str]

        """
        var_nums = []
        fun_names = []
        for line in self.line_list:
            split_line = line.split()
            for token in split_line:
                if PlaceholderManager.is_legal_var_name(token):
                    token_var_nums = \
                        PlaceholderManager.get_leg_var_var_nums(token)
                    fun_name = PlaceholderManager.get_leg_var_fun_name(token)
                    for var_num in token_var_nums:
                        if var_num not in var_nums:
                            var_nums.append(var_num)
                    if fun_name and fun_name not in fun_names:
                        fun_names.append(fun_name)

        return var_nums, fun_names

    def __add__(self, other):
        """
        define + of two SEO_Lista objects

        Parameters
        ----------
        other : SEO_Lista

        Returns
        -------
        SEO_Lista

        """
        assert self.num_bits == other.num_bits
        return SEO_Lista(self.num_bits,
                         self.line_list + other.line_list)

    def __iadd__(self, other):
        """
        define += for inplace addition of an SEO_Lista object to self

        Parameters
        ----------
        other : SEO_Lista

        Returns
        -------
        SEO_Lista

        """
        assert self.num_bits == other.num_bits
        self.line_list += other.line_list
        return self

    def __getitem__(self, item):
        """
        define self[item]

        Parameters
        ----------
        item : slice

        Returns
        -------
        SEO_Lista

        """
        return SEO_Lista(self.num_bits, self.line_list[item])

    def herm(self):
        """
        This method returns an EngLineList which is the Hermitian
        conjugate of self.

        Returns
        -------
        SEO_Lista

        """
        rev_li = list(reversed(self.line_list))
        lista = SEO_Lista(self.num_bits, rev_li)

        def minus(in_str):
            if in_str[0] == '-':
                new_str = in_str[1:]
            else:
                new_str = '-' + in_str
            return new_str

        for line_pos, line in enumerate(lista.line_list):
            split_line = line.split('\t')
            line_name = split_line[0]
            if line_name == 'DIAG':
                by_pos = split_line.index('BY')
                for k, token in enumerate(line[by_pos+1:]):
                    line[by_pos+1+k] = minus(token)
            elif line_name == "HAD2":
                pass
            elif line_name == "IF_M(":
                pass
            elif line_name == "}IF_M":
                pass
            elif line_name == "LOOP":
                pass
            elif line_name == "MEAS":
                pass
            elif line_name == "MP_Y":
                by_pos = split_line.index('BY')
                for k, token in enumerate(line[by_pos+1:]):
                    line[by_pos+1+k] = minus(token)
            elif line_name == "NEXT":
                pass
            elif line_name == 'NOTA':
                pass
            elif line_name == "PHAS":
                split_line[1] = minus(split_line[1])
            elif line_name == "P0PH":
                split_line[1] = minus(split_line[1])
            elif line_name == "P1PH":
                split_line[1] = minus(split_line[1])
            elif line_name == "PRINT":
                pass
            elif line_name == "ROTX":
                split_line[1] = minus(split_line[1])
            elif line_name == "ROTY":
                split_line[1] = minus(split_line[1])
            elif line_name == "ROTZ":
                split_line[1] = minus(split_line[1])
            elif line_name == "ROTN":
                for k in range(1, 4):
                    split_line[k] = minus(split_line[k])
            elif line_name == "SIGX":
                pass
            elif line_name == "SIGY":
                pass
            elif line_name == "SIGZ":
                pass
            elif line_name == "SWAP":
                pass
            else:
                assert False, \
                    "reading an unsupported line kind: " + line_name
            lista.line_list[line_pos] = '\t'.join(split_line)
        return lista

if __name__ == "__main__":
    def main():
        num_bits = 4
        file_prefix = 'io_folder/eng_file_line_list_test'
        emb = CktEmbedder(num_bits, num_bits)
        wr = SEO_writer(file_prefix, emb)
        wr.write_Rx(2, rads=np.pi/7)
        wr.write_Rx(1, rads='#2*.5')
        wr.write_Rx(1, rads='my_fun1#2')
        wr.write_Rn(3, rads_list=['#1', '-#1*3', '#3'])
        wr.write_Rx(1, rads='-my_fun2#2#1')
        wr.write_cnot(2, 3)
        wr.close_files()

        lili = SEO_Lista.eng_file_to_line_list(file_prefix, num_bits)
        lista = SEO_Lista(num_bits, lili)

        print("\nlista print")
        lista.print()
        nums, names = lista.get_var_nums_and_fun_names()
        print("lista's all_var_nums=\n", nums)
        print("lista's all_fun_names=\n", names)

        lista.write_eng_and_pic_files(file_prefix + '_ditto')

        print("\nlista[1:] print")
        lista[1:].print()

        lista_twice = lista + lista

        print("\nlista_twice print")
        lista_twice.print()
        nums, names = lista_twice.get_var_nums_and_fun_names()
        print("lista_twice's all_var_nums=\n", nums)
        print("lista_twice's all_fun_names=\n", names)

        lista_0 = SEO_Lista(num_bits)
        lista_0 += lista

        print("\nlista_0 print")
        lista_0.print()

        lista_herm = lista.herm()
        print('\nlista_herm print')
        lista_herm.print()

        lista = SEO_Lista(4)
        lista.append('write_cnot', [0, 1])
        lista.append('write_Rn', [2, [np.pi / 2, -np.pi / 2, np.pi / 3]])
        print('\n print 2 line lista')
        lista.print()
        sim = lista.simulate()
        sim.describe_st_vec_dict()

    main()
