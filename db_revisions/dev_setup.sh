#!/bin/sh

if [[ $1 == "" ]]
then
 echo "No arguments passed!"
 echo "The argument must be either reset or reset-then-seed"
 exit 0
fi

ACTION=$1

if [ $ACTION == "reset" ] 
then 
    #If only need to reset db
    poetry run alembic downgrade base
elif [ $ACTION == "reset-then-seed" ] 
then
    #First reset the db
    poetry run alembic downgrade base
    #Then upgrade it to head
    poetry run alembic upgrade head 
fi