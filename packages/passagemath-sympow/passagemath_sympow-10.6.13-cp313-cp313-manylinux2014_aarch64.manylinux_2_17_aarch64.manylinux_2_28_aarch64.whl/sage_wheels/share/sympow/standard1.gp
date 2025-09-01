allocatemem(2^28); \\ need 2^28 for 64-bit machines; else 2^27
L; X;
SP=mx+2;
default(seriesprecision,SP+1);
H=vector(SP);
{for(i=1,SP,H[i]=vector(N);
 for(j=1,N,if(i==1,if(j==1,H[1][1]=1,H[i][j]=H[i][j-1]+1.0/j),
           if(j==1,H[i][1]=H[i-1][1],H[i][j]=H[i][j-1]+H[i-1][j]/j*1.0))));}
Hf(n,k)=if(k==0,0,H[n][k])
ZETA(n)=if(n==1,Euler,zeta(n))
J(k,v)=if(k<0,(v-k-1)*J(k+1,v),\
                1.0*(-1)^k/k!/v*\
                exp(sum(n=1,SP,(-1)^n*(ZETA(n)/n)*v^n))*\
                (1+sum(n=1,SP,Hf(n,k)*v^n)))
sinv(k,v)=if(k==0,1/v,-1/k-sum(l=1,SP,v^l/k^(l+1)))
two1ms(k,v)=2^(1+k)*sum(l=0,SP,log(1/2)^l/l!*v^l)

{DERIV(M)=
 sum(i=0,poldegree(M,L),
        (deriv(polcoeff(M,i,L),X)+(i+1)*polcoeff(M,i+1,L)/X)*L^i)}
        
{ev(T,v,C)=U=0;
 for(i=0,mx,U+=(truncate(polcoeff(T,i,L)+O(X^C))*L^i));
 subst(subst(U,L,log(v)),X,v);}
