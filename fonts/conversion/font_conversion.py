# create a bit representation of a font
# using https://www.1001fonts.com/5by7-font.html - download as ttf file
# use https://stmn.itch.io/font2bitmap to convert to a bitmap - using 50 for the grid and the font size - and only 1 column

import json
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
image_path = 'fonts/conversion/5by7.regular.50x50x50.png'
output_file_dict = 'fonts/5by7.regular.dict.json'
output_file_bytes = 'fonts/5by7.regular.bytes.json'

image = mpimg.imread(image_path)

rows_per_char = 50
cols_per_char = 50
relevant_points_x = [15, 20, 25, 30, 35]
relevant_points_y = [10, 15, 20, 25, 30, 35, 40]  # take these points from the char image as the relevant points
### the font actually has many more chars - 396 all in all!
chars = ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~'

char_defs = {}
for ichar in range(len(chars)):
    start_row = ichar * rows_per_char
    print(f'====== {chars[ichar]} ==============')
    char_image = image[start_row : start_row + rows_per_char + 1]
    for iline, line in enumerate(char_image):
        line_rep = ''.join(['o' if x[0]>0 else '.' for x in line.tolist()])
        print(f'{iline:3} {line_rep}')
    # extract relevant points
    char_data = []
    for iy in relevant_points_y:
        char_line = []
        for ix in relevant_points_x:
            p = 1 if char_image[iy, ix][0] > 0 else 0
            char_line.append(p)
        char_data.append(char_line)
    print('--------------------')
    for iline, line in enumerate(char_data):
        line_rep = ''.join(['X' if x>0 else ' ' for x in line])
        print(f'{iline:3} {line_rep}')

    char_defs[chars[ichar]] = char_data

print(char_defs)

# write char_defs to file
with open(output_file_dict, 'w') as out:
    out.write(json.dumps(char_defs))

# # test read
# with open(output_file_dict, 'r') as inp:
#     test_read = json.load(inp)
# print(test_read['T'])

# convert to list of bytes
char_defs_bytes = {}
for c, data in char_defs.items():
    char_bytes = []
    for icol in range(5):
        byte_sum = 0
        for irow in range(7):
            p = data[irow][icol]
            if p > 0:
                byte_sum += 2**(6-irow)    ## lowest corresponds to smallest bits
        char_bytes.append(byte_sum)
    char_defs_bytes[c] = char_bytes


print('=====================')
# print(char_defs_bytes)


# write byte representation to disk?
with open(output_file_bytes, 'w') as out:
    out.write(json.dumps(char_defs_bytes))

# # test read
# with open(output_file_bytes, 'r') as inp:
#     test_read = json.load(inp)
# print(test_read['T'])

# plt.imshow(image)
# plt.show()