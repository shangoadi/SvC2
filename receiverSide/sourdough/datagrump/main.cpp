/*
 * main.c
 *
 *  Created on: Dec 2, 2016
 *      Author: root
 */

#include <pthread.h>

#include <iostream>
#include <list>
#include <string>
#include <unistd.h>
void* sender(void *parms);
void* receiver(void *parms);

int main(int argc, char *argv[])
{
	pthread_t senderThreadId, recvThreadId;
	std::cout << "Main is called" << std::endl;
	std::list<std::string> arguments;

	for (int i = 0; i < argc; i++) {
		arguments.push_back(argv[i]);
	}


	pthread_create(&recvThreadId, NULL,
	                           receiver, (void *)&arguments);

	pthread_create(&senderThreadId, NULL,
	                           sender, (void *)&arguments);


	while(1)
	{
		sleep(1);
	}
}


