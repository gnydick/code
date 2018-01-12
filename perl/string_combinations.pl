#!/usr/bin/perl
use strict;
use warnings FATAL => 'all';
$| = 1;

# All possible combinations of a string of characters

my $string = shift;
chomp $string;
my @chars = split(//, $string);

return_char("", @chars);



sub return_char {
    my ($prefix, @array) = @_;
    for (my $i = 0; $i < @array; $i++) {
        if (@array == 1) {
            print $prefix . $array[$i] . "\n";
        }
        my @newarray = @array;
        my $char = splice(@newarray, $i, 1);
        return_char($prefix . $char, @newarray);
    }

}
