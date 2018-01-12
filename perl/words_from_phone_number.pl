#!/usr/bin/perl
use strict;
use warnings FATAL => 'all';

# Define a function which takes in a phone number (7 numbers) and returns all of the words this could map to

use strict;
use warnings;
$| = 1;

my $phone = shift;
chomp $phone;

my %map;
$map{2} = [ 'a', 'b', 'c' ];
$map{3} = [ 'd', 'e', 'f' ];
$map{4} = [ 'g', 'h', 'i' ];
$map{5} = [ 'j', 'k', 'l' ];
$map{6} = [ 'm', 'n', 'o' ];
$map{7} = [ 'p', 'q', 'r', 's' ];
$map{8} = [ 't', 'u', 'v' ];
$map{9} = [ 'w', 'x', 'y', 'z' ];

my @nums = split(//, $phone);
my @chars;

doit(0, @nums);

sub doit {
    my ($index, @nums) = @_;
    if ($index < @nums) {
        my $num = $nums[$index];
        my @letters = get_letters($num);
        for my $letter (@letters) {
            $chars[$index] = $letter;
            doit($index + 1, @nums);
            print_word() if $index == @nums - 1;

        }
    }
}

sub get_letters {
    my $index = $_[0];
    return @{$map{$index}};
}

sub print_word {
    print join '', @chars;
    print "\n";
}
