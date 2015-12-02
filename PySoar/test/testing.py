def call_other():
    print 'other method called'

def func_test(url=""):
    if url == "":
        call_other()
    else:
        print url

func_test("http")
func_test()


# a = ['cruise', 'bla', 'cruise', 'cruise', 'thermal']
# print a.index('cruise', 0, 100)
# for index, item in enumerate(a):
#     if item == 'cruise':
#         print index, item

#
#  no_legs = 3
# indicators = ['jaja', 'neenee', 'twijfelachtig']
# pointwise_leg = []
#
# for leg in range(no_legs):
#     for indicator in indicators:
#         # print indicator
#         pointwise_leg.append({indicator: []})
#         # pointwise_leg[leg][indicator] = []
#
# print pointwise_leg