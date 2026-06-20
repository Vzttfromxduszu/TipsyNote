import request from "@/utils/request";
import type { LocationResponse } from "@/types/location";

export const reverseGeocode = async (
  lng: number,
  lat: number
): Promise<LocationResponse> => {
  const { data } = await request.get(
    "/location/reverse-geocode",
    {
      params: {
        lng,
        lat,
      },
    }
  );

  return data;
};