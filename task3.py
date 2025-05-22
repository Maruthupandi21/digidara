def prime():
    a=int (input("enter an input number:"))
    if a>1:
        for j in range(2,int(a/2)+1):
            if(a%j==0):
                print(a,"not prime number")
                break
            else:
                print(a,"is prime number")
    else:
        print(a,"is not a prime number")
prime()        
