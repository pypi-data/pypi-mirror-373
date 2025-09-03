#! /usr/bin/env libtbx.python
# -*- coding: utf-8 -*-
# =============================================================================

## @file af2parser
#
#  A simple parser/plotter for AF2 jobs


__author__ = "Grzegorz Chojnowski"
__author_email__ = "gchojnowski@embl-hamburg.com"
__date__ = "2022-02-21"
__updated__ = "2022-02-21"

import re, os, sys, glob

from optparse import OptionParser, OptionGroup, SUPPRESS_HELP


ROOT = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(2, ROOT)

try:
    import af2parser.version
    _version = af2plots.version.__version__
except:
    _version="dev"


from af2plots.plotter import plotter

lib_header="""
# af2parser(v%s): AF2 plots parser
"""%(_version)

def parse_args():
    """setup program options parsing"""
    parser = OptionParser(usage="Usage: af2parser [options]", version="af2parser %s"%_version)


    required_opts = OptionGroup(parser, "Required parameters")
    parser.add_option_group(required_opts)

    required_opts.add_option("--pkl_dir", action="store", \
                            dest="pkl_dir", type="string", metavar="DIRNAME", \
                  help="directory with AF2 model pickles", default=None)


    required_opts.add_option("--html_out", action="store", \
                            dest="html_out", type="string", metavar="DIRNAME", \
                            help="create html report: DIRNAME/report.html", default=None)


    required_opts.add_option("--out", action="store", \
                            dest="out", type="string", metavar="FILENAME", \
                  help="out plot(s) filename", default=None)

    required_opts.add_option("--test", action="store_true", dest="test", default=False, \
                  help="a simple test")

    (options, _args)  = parser.parse_args()
    return (parser, options)


def test():

    af2o = plotter()
    dd= af2o.parse_model_pickles(f'{ROOT}/../examples/PIAQ_test_af2mmer_dimer/input/')
    ff=af2o.plot_predicted_alignment_error(dd)
    #ff.savefig("plot_pae.png")
    ff=af2o.plot_plddts(dd)
    #ff.savefig("plot_plddt.png")
    ff = af2o.msa2fig(a3m_filenames=[f'{ROOT}/../examples/PIAQ_test_af2mmer_dimer/input/msas/A/bfd_uniclust_hits.a3m']*5)
    #ff.savefig("plot_msa.png")



def main():

    print(lib_header)

    (parser, options) = parse_args()

    print( " ==> Command line: af2parser %s" % (" ".join(sys.argv[1:])) )

    if options.test:
        test()
        print
        exit(0)


    if options.html_out and options.pkl_dir:

        af2o = plotter()
        af2o.make_html_report(options.pkl_dir, options.html_out)

        return

    # this is more an example, but you can use it
    # to parse your af2 job data too
    if options.pkl_dir:

        af2o = plotter()
        fig_dict = {}

        dd= af2o.parse_model_pickles(options.pkl_dir)
        ff=af2o.plot_predicted_alignment_error(dd)
        fig_dict['pae'] = ff

        ff=af2o.plot_plddts(dd)
        fig_dict['plddt'] = ff

        # this wil try to plot MSA too
        fns=[]
        for dirname,_,_ in os.walk(options.pkl_dir):
            _fn = glob.glob("%s/bfd*.a3m" % dirname)
            if _fn: fns.extend(_fn)

        if fns:
            ff = af2o.msa2fig(a3m_filenames=fns)
            fig_dict['msa'] = ff

        # does the same as above in a single line
        if 0: fig_dict = af2o.parse_all_fig_data(options.pkl_dir)

        # write matplolib plot objects to files
        if options.out:
            for suffix, ff in fig_dict.items():
                ofn = options.out.split('.')[0]+f"_{suffix}.png"
                ff.savefig(ofn)
                print(f'Wrote {ofn}')


        return


    parser.print_help()
    print
    exit(0)


if __name__=="__main__":
    main()

