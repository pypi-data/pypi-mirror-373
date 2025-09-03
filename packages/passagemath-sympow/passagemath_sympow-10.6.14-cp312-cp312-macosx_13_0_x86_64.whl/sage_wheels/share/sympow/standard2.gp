
P=sum(k=0,N,sum(l=1,mx+1,-(-1)^l/(l-1)!*polcoeff(F(k),-l,X)*L^(l-1))*X^k);
K=40; Ds=vector(K); Ds[1]=DERIV(P); for(i=2,K,Ds[i]=DERIV(Ds[i-1]));

ieee(x)=(round(x<<53)*1.0)>>53
{IEEE(x)=if(x==0,return(0));if(length(x)<2,return(0));
         y=ceil(log(abs(x))/log(2));ieee(x/2^y)*2^y;}
{QD(x)=local(A);A=[IEEE(x),0,0,0];A[2]=IEEE(x-A[1]);A[3]=IEEE(x-A[1]-A[2]);
 A[4]=IEEE(x-A[1]-A[2]-A[3]); A=precision(A,18);
 print(A[1]); print(A[2]); print(A[3]); print(A[4]);}

 
{doit(x,C)=print("AT ",x); QD(ev(P,x,C));
 for(d=1,35,print("DERIV ",d); QD(ev(Ds[d]/d!,x,C)));}
ch(x,C)=ev(P,x,C)-ev(P,x,C+20)

setup(a,b)=for(i=0,31,doit(2^a+2^a*i/32,b));
print("About to find TOO_BIG"); \\ ends up in /dev/null
MM=100; while(log(10^(-70)+abs(ev(P,MM,N)))>-148,MM*=1.1);
write1(PARAMDATAFILE,STR,",",precision(IEEE(MM),18));
print("Now working backwards..."); \\ ends up in /dev/null
l=-10; while(log(10^(-70)+abs(ch(2^l,20)))<-148,l+=1); l-=1; s=l;
write1(PARAMDATAFILE,",",l-5); n=20;
print("Starting to write mesh files"); \\ ends up in /dev/null
