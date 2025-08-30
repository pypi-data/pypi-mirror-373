while(2^l<MM,while(log(10^(-70)+abs(ch(2*2^l,n)))>-148,n+=5);setup(l,n);l+=1);
write(PARAMDATAFILE,",",l-s);
coeffs(j)=for(i=0,19,print("PS ",i);QD(polcoeff(polcoeff(P,j,L),i,X)));
coeffO(j)=\
for(i=0,9,print("PSL ",2*i+1);QD(polcoeff(polcoeff(P,j,L),2*i+1,X)));
coeffE(j)=\
for(i=0,9,print("PSL ",2*i);QD(polcoeff(polcoeff(P,j,L),2*i,X)));
