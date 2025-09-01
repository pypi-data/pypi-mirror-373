#include <mpi.h>
#include <stdio.h>

int main(int argc, char** argv) 
{
	// Initialize the MPI environment
	MPI_Init(NULL, NULL);

	// Get the number of processes
	int size;
	MPI_Comm_size(MPI_COMM_WORLD, &size);

	// Get the rank of the process
	int rank;
	MPI_Comm_rank(MPI_COMM_WORLD, &rank);

	// Get the name of the processor
	char processor_name[MPI_MAX_PROCESSOR_NAME];
	int name_len;
	MPI_Get_processor_name(processor_name, &name_len);

	if(rank==0)
	{
		printf("I am the head hancho. Hello world from processor %s, rank %d out of %d processors\n", processor_name, rank, size);
		for(int i=0;i<size;i++)
		{
			//http://www.mpich.org/static/docs/v3.1.x/www3/MPI_Send.html
			MPI_Send(&ping_pong_count,//  const void *buf                     
			         1,               //         int count       
			         MPI_INT,         //MPI_Datatype datatype            
			         partner_rank,    //         int dest                 
			         0,               //         int tag      
			         MPI_COMM_WORLD); //    MPI_Comm comm                    
		}
	}
	else
	{
		printf("Hello world from processor %s, rank %d out of %d processors\n", processor_name, rank, size);
	}

	// Finalize the MPI environment.
	MPI_Finalize();
}


