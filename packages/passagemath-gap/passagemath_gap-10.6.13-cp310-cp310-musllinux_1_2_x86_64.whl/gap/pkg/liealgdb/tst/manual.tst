#
gap> L := AllNonSolvableLieAlgebras( GF(4), 4 );
<Collection of nonsolvable Lie algebras with dimension 4 over GF(2^2)>
gap>  e := Enumerator( L );
<enumerator>
gap> for i in e do Print( Dimension( LieSolvableRadical( i )), "\n" ); od;
0
1
gap> AsList( L );
[ W(1;2), W(1;2)^{(1)}+GF(4) ]
gap> Dimension( LieCenter( last[2] ));
1

#
gap> L := AllNonSolvableLieAlgebras( GF(5^20), 6 );
<Collection of nonsolvable Lie algebras with dimension 6 over GF(5^20)>
gap> e := Enumerator( L );
<enumerator>
gap> Length( last );
95367431640638
gap> Dimension( LieDerivedSubalgebra( e[462468528345] ));
5

#
gap> L := AllNonSolvableLieAlgebras( GF(3), 6 );
<Collection of nonsolvable Lie algebras with dimension 6 over GF(3)>
gap>  e := Iterator( L );
<iterator>
gap> dims := [];;
gap> for i in e do Add( dims, Dimension( LieSolvableRadical( i ))); od;
gap> dims;
[ 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3 ]
gap> AsList( L );
[ sl(2,3)+sl(2,3), sl(2,GF(9)), sl(2,3)+solv([ 1 ]), sl(2,3)+solv([ 2 ]), 
  sl(2,3)+solv([ 3, 0*Z(3) ]), sl(2,3)+solv([ 3, Z(3)^0 ]), 
  sl(2,3)+solv([ 3, Z(3) ]), sl(2,3)+solv([ 4, 0*Z(3) ]), 
  sl(2,3)+solv([ 4, Z(3) ]), sl(2,3)+solv([ 4, Z(3)^0 ]), sl(2,3):(V(1)+V(0)),
  sl(2,3):V(2), sl(2,3):H, sl(2,3):<x,y,z|[x,y]=y,[x,z]=z>, 
  sl(2,3):V(2,0*Z(3)), sl(2,3):V(2,Z(3)), W(1;1):O(1;1), W(1;1):O(1;1)*, 
  sl(2,3).H(0), sl(2,3).H(1), sl(2,3).(GF(3)+GF(3)+GF(3))(1), 
  sl(2,3).(GF(3)+GF(3)+GF(3))(2) ]

#
gap> SolvableLieAlgebra( Rationals, [4,6,1,2] );
<Lie algebra of dimension 4 over Rationals>

#
gap> NilpotentLieAlgebra( GF(3^7), [ 6, 24, Z(3^7)^101 ] );
<Lie algebra of dimension 6 over GF(3^7)>

#
gap> L:= SolvableLieAlgebra( Rationals, [4,14,3] );
<Lie algebra of dimension 4 over Rationals>
gap>  LieAlgebraIdentification( L );
rec( isomorphism := CanonicalBasis( <Lie algebra of dimension 
    4 over Rationals> ) -> [ v.3, (-1)*v.2, v.1, (1/3)*v.4 ], 
  name := "L4_14( Rationals, 1/3 )", parameters := [ 1/3 ] )
