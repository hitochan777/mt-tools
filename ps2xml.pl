#!/usr/bin/env perl
# You can run this program to convert constituency parse trees to dependency trees as follows:
# perl ps2xml.pl -l English -k 1 -rule_file Sexp_rule/Sexp_rule_E_sem.txt > output_file 
# The conversion rule file Sexp_rule/Sexp_rule_E_sem.txt is made based on 
# @phdthesis{Collins:1999,
# author = {Collins, Michael},
# title = {Head-Driven Statistical Models for Natural Language Parsing},
# school = {University of Pennsylvania},
# year = {1999},
# }
# and modified slightly so as to use semantic head.

use strict;
use FindBin qw($Bin);
use lib "$Bin/../lib";

use Getopt::Long;
use FileHandle;
use XML::Writer;
use Sexp;
use Lemmatize;
use utf8;
binmode(STDIN, ':encoding(utf8)');
binmode(STDOUT, ':encoding(utf8)');

my (%opt) = (index => 'j_data',
             output_mode => 'tsv',
            );
GetOptions(\%opt, 'verbose', 'language=s', 'index=s', 'keep_punctuation=i', 'rule_file=s', 'output_mode=s');

$opt{output_mode} =~ tr/[A-Z]/[a-z]/;

die "Invalid language: $opt{language}\n" if ($opt{language} !~ /(English|Chinese|French|NICT)/);

$opt{fh} = *STDIN;
my $s = new Sexp(\%opt);        # new FileHandle($ARGV[0])
my $lemma = new Lemmatize();

my %pf_order = (dpnd => 0, pnum => 1, cat => 2, f => 99); # print order of phrase attributes
my %wf_order = (lem => 0, read => 1, pos => 2, POS => 3, content_p => 4, abs_wnum => 5); 
# print order of word attributes

my %HONORIFICS = map({$_ => 1} qw(Adj. Adm. Adv. Asst. Bart. Brig. Bros. Capt. Cmdr. Col. Comdr. Con. Cpl. Dr. Ens. Gen. Gov. Hon. Hosp. Insp. Lt. M. MM. Maj. Messrs. Mlle. Mme. Mr. Mrs. Ms. Msgr. Op. Ord. Pfc. Ph. Prof. Pvt. Rep. Reps. Res. Rev. Rt. Sen. Sens. Sfc. Sgt. Sr. St. Supt. Surg.));

my $writer = new XML::Writer(OUTPUT => *STDOUT, DATA_MODE => 'true', DATA_INDENT => 2);

my $old_id = "";
my $sentence_count = 0;
if ($opt{output_mode} eq 'xml' && !$opt{verbose}) {
    $writer->xmlDecl('utf-8');
    $writer->startTag('article');
}

while ($s->read_one_sexp()) {

    $s->phrase_structure_category();
    $s->leaf_reduction();
    $s->modify_temporal_noun();

    if ($opt{verbose}) {
        print "============================\n"; 
        print "$s->{id}\n";
        $s->print_tree();
    }

    $s->ps2dependency($opt{verbose}, $opt{language});

    if ($opt{verbose}) {
        print "----------------------------\n";
        $s->print_tree2();
        print "----------------------------\n";
    }

    if (!$opt{verbose}) {
        if ($old_id eq $s->{id}) {
            $sentence_count++;
        } else {
            if ($opt{output_mode} eq 'xml') {
                $writer->endTag() if ($old_id ne ""); # sentence
                $writer->startTag('sentence', id => $s->{id});
            }
            $sentence_count = 0;
        }
        $old_id = $s->{id};
        &TreeNumbering($s->{root}, 0);
        if ($opt{output_mode} eq 'xml') {
            $writer->startTag($opt{index}, prob => $s->{prob});
        } elsif ($opt{output_mode} eq 'tsv') {
            print "# ID=$s->{id} SCORE=$s->{prob}\n";
        }
        &PrintTree($s->{root}, -1, $opt{language}, undef, \%opt);
        if ($opt{output_mode} eq 'xml') {
            $writer->endTag();  # j_data
        } elsif ($opt{output_mode} eq 'tsv') {
            print "\n";
        }
    }
}

if ($opt{output_mode} eq 'xml' && !$opt{verbose}) {
    $writer->endTag();          # sentence
    $writer->endTag();          # article
    $writer->end();
}


######################################################################
sub TreeNumbering {
    my ($ref, $num) = @_;

    if (@{$ref->{pre_children}}) {
        for my $c (@{$ref->{pre_children}}) {
            $num = &TreeNumbering($c, $num);
        }
    }

    $ref->{num} = $num;
    $num ++;

    if (@{$ref->{post_children}}) {
        for my $c (@{$ref->{post_children}}) {
            $num = &TreeNumbering($c, $num);
        }
    }
    return $num;
}

######################################################################
sub PrintTree {
    my ($ref, $head_num, $language, $srole, $opt) = @_;
    my ($i, $word, $pos, $POS, $lem, $content_p, $abs_wnum);

    if (@{$ref->{pre_children}}) {
        for my $c (@{$ref->{pre_children}}) {
            &PrintTree($c, $ref->{num}, $language, 
                          $ref->{atom}[0] eq 'S1' && $c->{atom}[0] eq 'NP' ? 'sbj' : '', $opt); # mark subject
        }
    }

    # print "$head_num $ref->{num}\n";

    my (%pf);
    $pf{dpnd} = $head_num;      # 係り先
    $pf{pnum} = $ref->{num};    # 自分のphrase番号
    $pf{cat} = $ref->{atom}[0];	# phrase category
    $pf{cat} =~ s/\/.+//;       # "CC/and"など
    $pf{f} = join(":", @{$ref->{atom}});
    # $pf{f} =~ s/\/[\d]+//g; 
    $pf{role} = $srole if $language eq "English"; # syntactic role

    if ($opt->{output_mode} eq 'xml') {
        $writer->startTag('phrase', map({$_ => $pf{$_}} sort {$pf_order{$a} <=> $pf_order{$b}} keys %pf));
    }

    # word
    my @accum_atom; 
    for ($i = 0; $i < @{$ref->{atom}}; $i++) {
        push(@accum_atom, $ref->{atom}[$i]);
        if ($ref->{atom}[$i] =~ /^(.+?)\/(.+)\/(.+?)$/) {
            $pos = $1;
            $word = $2;
            $abs_wnum = $3;
            $lem = $word;
            $POS = join(":", @accum_atom);
            @accum_atom = ();

            if ($language eq "English") {
                if ($abs_wnum == 0 && $word =~ /^[A-Z][a-z]*$/) { # upper case at the beginning
                    unless ($pos =~ /^NNP/ || defined($HONORIFICS{$word})) { # isn't proper noun or honorific
                        $word = lc($word);
                    }
                }
                $lem = $word;
                my (@lems) = $lemma->lemmatize($lem, $pos);
                $lem = $lems[0] if (@lems > 0);
            }

            if (($language eq "English" && $pos =~ /^(IN|TO|MD|CC|DT)\*?/) ||
                ($language eq "Chinese" && $pos =~ /^(P|CS)\*?/)) {
                $content_p = 0;
            } elsif (($language eq "English" && $pos =~ /^(\.|\,|\?|\!|\:|\-LRB\-|\-RRB\-|\'\'|\`\`)\*?/) ||
                     ($language eq "Chinese" && $pos =~ /^(PU)\*?/)) {
                $content_p = -1;
            } else {
                $content_p = 1;
            }
            my %wf = (lem => $lem,
                      read => "",
                      pos => $pos,
                      POS => $POS,
                      content_p => $content_p,
                      abs_wnum => $abs_wnum,
                     );
            if ($opt->{output_mode} eq 'xml') {
                $writer->startTag('word', map({$_ => $wf{$_}} sort {$wf_order{$a} <=> $wf_order{$b}} keys %wf));
                $writer->characters($word);
                $writer->endTag();
            } elsif ($opt->{output_mode} eq 'tsv') {
                printf "%d\t%d\t%s\t%s\t%s\t%d\t%s\t%s\t%s\n",
                    $abs_wnum, $pf{dpnd}, $word, $lem, $pos, $content_p, $pf{cat}, $pf{type}, $POS;
            }
        }
    }

    if ($opt->{output_mode} eq 'xml') {
        $writer->endTag();          # phrase
    }

    my ($srole_done);
    if (@{$ref->{post_children}}) {
        for my $c (@{$ref->{post_children}}) {
            if (!$srole_done && # the first NP is an object
                $ref->{atom}[0] eq 'S1' and $c->{atom}[0] eq 'NP') {
                $srole = 'obj';
                $srole_done++;
            } else {
                $srole = '';
            }
            &PrintTree($c, $ref->{num}, $language, $srole, $opt);
        }
    }
}

######################################################################

