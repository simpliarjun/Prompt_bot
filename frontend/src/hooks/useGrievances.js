import { useQuery, useMutation, useQueryClient, keepPreviousData } from '@tanstack/react-query';
import {
  listGrievances,
  getGrievance,
  createGrievance,
  updateGrievance,
  deleteGrievance,
  getGrievanceStats,
  generateGrievance,
  exportPdf,
} from '../api/endpoints';

// ---- Queries ----

export function useGrievances(params = {}) {
  return useQuery({
    queryKey: ['grievances', params],
    queryFn: () => listGrievances(params),
    placeholderData: keepPreviousData,
  });
}

export function useGrievance(id) {
  return useQuery({
    queryKey: ['grievance', id],
    queryFn: () => getGrievance(id),
    enabled: !!id,
  });
}

export function useGrievanceStats() {
  return useQuery({
    queryKey: ['grievanceStats'],
    queryFn: getGrievanceStats,
  });
}

// ---- Mutations ----

export function useGenerateGrievance() {
  return useMutation({
    mutationFn: generateGrievance,
  });
}

export function useCreateGrievance() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createGrievance,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['grievances'] });
      qc.invalidateQueries({ queryKey: ['grievanceStats'] });
    },
  });
}

export function useUpdateGrievance() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => updateGrievance(id, data),
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['grievance', vars.id] });
      qc.invalidateQueries({ queryKey: ['grievances'] });
      qc.invalidateQueries({ queryKey: ['grievanceStats'] });
    },
  });
}

export function useDeleteGrievance() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: deleteGrievance,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['grievances'] });
      qc.invalidateQueries({ queryKey: ['grievanceStats'] });
    },
  });
}

export function useExportPdf() {
  return useMutation({
    mutationFn: async (id) => {
      const response = await exportPdf(id);
      const blob = response.data;
      const disposition = response.headers['content-disposition'] || '';
      const match = disposition.match(/filename="?(.+?)"?$/);
      const filename = match?.[1] || `grievance_${id}.pdf`;

      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    },
  });
}
