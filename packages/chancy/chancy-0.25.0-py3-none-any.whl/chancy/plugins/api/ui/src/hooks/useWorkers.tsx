import {useQuery} from '@tanstack/react-query';

export interface Worker {
  worker_id: string;
  tags: string[];
  queues: string[];
  last_seen: string;
  expires_at: string;
  is_leader: boolean;
}

export function useWorkers(url: string | null) {
  return useQuery<Worker[]>({
    queryKey: ['workers', url],
    queryFn: async () => {
      const response = await fetch(`${url}/api/v1/workers`);
      return await response.json();
    },
    refetchInterval: 10000,
    enabled: url !== null
  });
}