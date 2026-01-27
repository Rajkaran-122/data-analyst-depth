import React, { useMemo } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef } from 'ag-grid-community';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css'; // We overlap this with our custom dark theme in global css

interface DataGridProps {
    data: any[] | undefined;
    isLoading: boolean;
}

export function DataGrid({ data, isLoading }: DataGridProps) {

    // Dynamic column generation
    const columnDefs = useMemo<ColDef[]>(() => {
        if (!data || data.length === 0) return [];
        const firstRow = data[0];
        return Object.keys(firstRow).map(key => ({
            field: key,
            filter: true,
            sortable: true,
            resizable: true,
        }));
    }, [data]);

    const defaultColDef = useMemo(() => ({
        flex: 1,
        minWidth: 100,
    }), []);

    if (isLoading) {
        return (
            <div className="h-full w-full flex items-center justify-center bg-muted/20">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
        );
    }

    if (!data) {
        return (
            <div className="h-full w-full flex items-center justify-center bg-muted/20 text-muted-foreground">
                Run a query to see results
            </div>
        );
    }

    return (
        <div className="h-full w-full ag-theme-alpine-dark">
            <AgGridReact
                rowData={data}
                columnDefs={columnDefs}
                defaultColDef={defaultColDef}
                pagination={true}
                paginationPageSize={50}
                animateRows={true}
            />
        </div>
    );
}
