#!/usr/bin/perl

use strict;
use warnings;
use Data::Dumper;

# TicTacToe CPU vs CPU


my @row1 = ("_","_","_");
my @row2 = ("_","_","_");
my @row3 = ("_","_","_");

my @board = ([@row1], [@row2], [@row3]); 


my $piece = "X";

for (my $i=0; $i<9; $i++) {
  random_move($piece);
  if ($piece eq "X") {
    $piece = "O";
  } else {
    $piece = "X";
  }
  print_board();
  
  my $winner = check_for_winner();
  if ($winner) {
    print 'Winner: '.$winner."\n\n\n";
    exit(0);
  }
  
  
}
print 'No winner!'."\n\n\n";

sub print_board {
  for my $row (@board) {
    for my $col (@{$row}) {
      print $col.' ';
    }
    print "\n";
  }
  print "\n";
}

sub random_move {
  my $piece = shift(@_);
  #print 'piece '.$piece."\n";
  my $spot = "none";
  while ($spot eq "none") {
    my $row = int(rand(3));
    my $col = int(rand(3));
    if ($board[$row][$col] eq "_") {
      $board[$row][$col] = $piece;
      $spot = $piece;
    }
  }
  
}

sub check_for_winner{
  my $winner = 'none';
  # check rows,
  for my $row (@board) {
    if ($$row[0] eq $$row[1] & $$row[1] eq $$row[2]) {
      if ($$row[0] ne '_') {
        $winner = $$row[0];
        return $winner;
      }
    }
  }
     
  # check cols
  for (my $i = 0; $i < 3 ; $i++) {
    if ($board[0][$i] eq $board[1][$i] & $board[1][$i] eq $board[2][$i]) {
      if ($board[0][$i] ne '_') {
        $winner = $board[0][$i];
        return $winner;
      }
    }
  }  
  
  # check diag
  
    if ($board[0][0] eq $board[1][1] & $board[1][1] eq $board[2][2]) {
      if ($board[0][0] ne '_') {
        $winner = $board[0][0];
        return $winner;
      }
    }
    
    if ($board[2][0] eq $board[1][1] & $board[1][1] eq $board[0][2]) {
      if ($board[2][0] ne '_') {
        $winner = $board[2][0];
        return $winner;
      }
    }
    
}

