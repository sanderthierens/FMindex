import pandas as pd
from os import path
import math
import time

CHARS = ["A", "C", "G", "T", "$"]
LONG_TAB = "\t\t"


class ReadMapper:

    def __init__(self, file, sf_OT, sf_SA):
        self.file = file
        self.sf_OT = sf_OT
        self.sf_SA = sf_SA

        # Reading in occurrence table
        try:
            occ_path = path.join(self.file, self.file + ".occ")
            self.occ = pd.read_csv(occ_path, delim_whitespace=True, header=None, names=CHARS)

            # Reading in bwt
            bwt_path = path.join(self.file, self.file + ".bwt")
            with open(bwt_path) as f:
                self.bwt = list(f.readline())

            sa_path = path.join(self.file, self.file + ".sa")
            with open(sa_path) as f:
                self.sa = [int(line.rstrip()) for line in f]

            self.reverse = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}

            A_counts = self.bwt.count("A")
            C_counts = self.bwt.count("C")
            G_counts = self.bwt.count("G")
            T_counts = self.bwt.count("T")

            count_path = path.join(self.file, self.file + ".counts")
            with open(count_path) as f:
                self.counts = pd.Series([int(line.rstrip()) for line in f], index=CHARS)

            self.counts_sep = pd.Series([A_counts, C_counts, G_counts, T_counts, 1], index=CHARS)

        except FileNotFoundError as e:
            print(e)
            print("Currently looking for file: " + occ_path)
            print("Make sure your data files are stored under a parent directory with the same name")

    def revers_pattern(self, pattern):
        l = list(pattern)
        new_l = []
        for i in l:
            new_l.insert(0, self.reverse[i])
        return new_l

    def O(self, theta, k):
        try:

            nearest_occ_index = round(k / self.sf_OT)
            if nearest_occ_index == len(self.occ):
                nearest_occ_index += -1

            if nearest_occ_index > (k/self.sf_OT):
                direction = -1
            else:
                direction = 1

            nearest_occ_value = self.occ[theta].iloc[nearest_occ_index]
            iter_value = nearest_occ_value
            iter_index = nearest_occ_index*self.sf_OT
            while iter_index != k:
                if (direction == 1 and self.bwt[iter_index] == theta) or (direction == -1 and self.bwt[iter_index-1] == theta):
                    iter_value += direction
                iter_index += direction

            return iter_value
        except KeyError:
            print("Character " + theta + " is not a valid character")

    def LF(self, index):
        # get occurence of index
        l_char = self.bwt[index]
        if l_char == '$':
            return len(self.bwt)-1
        occ_index = self.O(l_char, index)

        return self.counts[l_char] + occ_index

    def SA(self, index):
        if index % self.sf_SA == 0:
            return self.sa[int(index/self.sf_SA)]
        count = 0
        while index % self.sf_SA != 0:
            index = self.LF(index)
            count += 1
        return self.sa[int(index/self.sf_SA)] + count

    def get_nextMatch(self, i, char_to_match):
        if self.bwt[i] != char_to_match:
            return None
        return self.LF(i)

    def exactMatches(self, pattern):
        p = list(pattern)

        index = len(p)-1
        first_char = p[index]
        start = self.counts[first_char]
        end = start + self.counts_sep[first_char]
        possible = list(range(start, end))

        while possible and index > 0:
            index += -1
            match_char = p[index]
            before_occ = self.O(match_char, possible[0])
            end_occ = self.O(match_char, possible[len(possible)-1]+1)
            match_occ = list(range(before_occ, before_occ + (end_occ-before_occ)))
            # print(match_occ)
            possible = [self.counts[match_char] + i for i in match_occ]
            # print(possible)
            # print(index)
        #print("result")
        return [self.SA(index) for index in possible]
        #
        # index = len(p)-1
        # first_char = p[index]
        # start = self.counts[first_char]
        # end = start + self.counts_sep[first_char]
        # possible = list(range(start, end))
        #
        # result = []
        # print("possible")
        # print(possible)
        # second_char = p[index-1]
        # before_occ = self.O(second_char, start)
        # end_occ = self.O(second_char, end+1)
        # next_list = list(range(before_occ, (before_occ) + (end_occ-before_occ) ))
        # print(next_list)
        # print(before_occ)
        # print(end_occ)
        # next_possible = [self.counts[second_char] + i for i in next_list]
        # print(next_possible)
        #
        # print("third")
        # third_character = p[index-2]
        # print(third_character)
        # print(next_possible[0])
        # print(next_possible[len(next_possible)-1])
        # before_occ = self.O(third_character, next_possible[0])
        # end_occ = self.O(third_character, next_possible[len(next_possible)-1]+1)
        # print(before_occ)
        # print(end_occ)
        # next_list = list(range(before_occ, (before_occ) + (end_occ-before_occ) ))
        # print("next list")
        # print(next_list)
        #
        # next_possible = [self.counts[third_character] + i for i in next_list]
        # print(next_possible)
        # print(self.SA(next_possible[0]))
        # # third_char = p[index-2]
        # # before_occ = self.O(third_char, start)
        # # end_occ = self.O(third_char, end+1)
        # # next_list = list(range(before_occ+1, (before_occ+1) + (end_occ-before_occ) ))
        # # print(next_list)
        # # print(before_occ)
        # # print(end_occ)
        #
        #
        # for i in possible:
        #     j = index
        #     k = i
        #     j += -1
        #     while j >= 0:
        #         if self.bwt[k] != p[j]:
        #             break
        #         k = self.LF(k)
        #         j += -1
        #     if j < 0:
        #         result.append(k)
        # return [self.SA(index) for index in result]

    def get_closest(self, l1, l2, r_size, insert_size):
        closest_value = math.inf
        for i in l1:
            for j in l2:
                if abs(abs(i-(j + r_size))-insert_size) <= closest_value:
                    closest = (i, j)
                    closest_value = abs(abs(i-(j + r_size))-insert_size)

        return closest, closest_value

    def bestPairedMatch(self, s1, s2, insert_size=800):
        s1_reverse = self.revers_pattern(s1)
        s2_reverse = self.revers_pattern(s2)

        list_s1 = self.exactMatches(s1)
        list_s2 = self.exactMatches(s2)
        list_s1_r = self.exactMatches(s1_reverse)
        list_s2_r = self.exactMatches(s2_reverse)

        f_closest = 0
        r_closest = 0
        if list_s1 and list_s2_r:
            f_closest, f_closest_val = self.get_closest(list_s1, list_s2_r, len(s2_reverse), insert_size)
        if list_s2 and list_s1_r:
            r_closest, r_closest_val = self.get_closest(list_s2, list_s1_r, len(s1_reverse), insert_size)
            r_closest = (r_closest[1], r_closest[0])
        if f_closest == 0 and r_closest == 0:
            raise Exception("Sorry, no matches found")
        elif r_closest == 0:
            result = f_closest
            forward = True
        elif f_closest == 0:
            result = r_closest
            forward = False
        else:
            if f_closest_val <= r_closest_val:
                result = f_closest
                forward = True
            else:
                result = r_closest
                forward = False

        return result[0], result[1], forward

    def map(self, fasta, sam, insert_size=800):
        f = open(sam, "w")

        # Write header
        f.write("@SQ\t\t" + "SN:" + self.file + "\t\tLN:" + str(self.counts['$']))
        f.write("\n@PG\t\tID:" + self.__class__.__name__)

        # Start pairwise alignment
        read_file = open(fasta, 'r')
        while True:
            # Get next line from file
            s1_h = read_file.readline()
            # if line is empty
            if not s1_h:
                # end of file is reached
                break
            s1 = read_file.readline()
            s2_h = read_file.readline()
            s2 = read_file.readline()
            s1_h = s1_h.replace('>','').replace('\n','')
            s2_h = s2_h.replace('>','').replace('\n','')
            s1 = s1.replace('\n','')
            s2 = s2.replace('\n','')
            s1_pos, s2_pos, forward = self.bestPairedMatch(s1, s2, insert_size)

            # bitwise FLAGS
            if forward:
                s1_strand = 0
                s2_strand = 16
            else:
                s1_strand = 16
                s2_strand = 0

            # Content of SAM file
            s1_sam = LONG_TAB.join([("\n" + s1_h), str(s1_strand), self.file, str(s1_pos+1), "255", (str(len(s1))+"M"),
                                    "=", "0", "0", "*", "*"])
            s2_sam = LONG_TAB.join([("\n" + s2_h), str(s2_strand), self.file, str(s2_pos+1), "255", (str(len(s2))+"M"),
                                    "=", "0", "0", "*", "*"])
            f.write(s1_sam)
            f.write(s2_sam)

        read_file.close()
        f.close()



demoRM = ReadMapper("demo", 4, 2)
print([demoRM.SA(index) for index in range(11)])
# print([demoRM.LF(index) for index in range(11)])
# print([demoRM.O('A', index) for index in range(11)])
# print([demoRM.O('C', index) for index in range(11)])
# print([demoRM.O('G', index) for index in range(11)])
# print([demoRM.O('T', index) for index in range(11)])
# print([demoRM.O('$', index) for index in range(11)])
print(demoRM.exactMatches('GAT'))
print(demoRM.exactMatches('AT'))
# print(demoRM.bestPairedMatch('GCA', 'TA', 8))
# print(demoRM.bestPairedMatch('TGC', 'TA', 8))
# demoRM.map("demo/demo.reads.fasta", "firsttest.sam")
#
# indices = [0, 247380, 685559, 704037, 1502653, 2759112, 3187255, 4870265]
# t0 = time.time()
CP001363 = ReadMapper("CP001363", 128, 32)
#
# # There seems to be an ambiguity in this one where two possible sets of positons are both
# # equally close to the insertion size
print(CP001363.bestPairedMatch('TAAGTAACGATA', 'TCAAGCTATA'))
t0 = time.time()
CP001363.map("CP001363/CP001363.reads.fasta", "custom.sam")
t1 = time.time()
print(t1-t0)


