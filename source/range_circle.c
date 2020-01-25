static guint calculate_footprint(GtkSatMap * satmap, sat_t * sat)
{
    guint           azi;
    gfloat          sx, sy, msx, msy, ssx, ssy;
    gdouble         ssplat, ssplon, beta, azimuth, num, dem;
    gdouble         rangelon, rangelat, mlon;
    gboolean        warped = FALSE;
    guint           numrc = 1;

    /* Range circle calculations.
     * Borrowed from gsat 0.9.0 by Xavier Crehueras, EB3CZS
     * who borrowed from John Magliacane, KD2BD.
     * Optimized by Alexandru Csete and William J Beksi.
     */

    #satellite geodetic latitude and longitude * de2ra = lat and longitude in radians
    ssplat = sat->ssplat * de2ra;
    ssplon = sat->ssplon * de2ra;

    #xkmper = radius of earth in km                                    pos->w is magnitude of pos by pythagoras?  altitude?
    $sat->footprint = 2.0 * Predict::xkmper * acos (Predict::xkmper/$sat->pos->w);
    beta = (0.5 * sat->footprint) / xkmper;
    #beta is acos(xmper/magnitude of pos)

    for (azi = 0; azi < 180; azi++)
    {
        azimuth = de2ra * (double)azi; #azimuth in radians

        range latitude = sin-1(sin(satellite lat) * cos(beta which is what?) * cos azimuth * sin beta * cos(satellite latitude))
        rangelat = asin(sin(ssplat) * cos(beta) + cos(azimuth) *
                        sin(beta) * cos(ssplat));
        num = cos(beta) - (sin(ssplat) * sin(rangelat));
        dem = cos(ssplat) * cos(rangelat);

        if (azi == 0 && north_pole_is_covered(sat))
            rangelon = ssplon + pi;
        else if (fabs(num / dem) > 1.0)
            rangelon = ssplon;
        else
        {
            if ((180.0 - azi) >= 0)
                rangelon = ssplon - arccos(num, dem);
            else
                rangelon = ssplon + arccos(num, dem);
        }

        while (rangelon < -pi)
            rangelon += twopi;

        while (rangelon > (pi))
            rangelon -= twopi;

        rangelat = rangelat / de2ra;
        rangelon = rangelon / de2ra;

        /* mirror longitude */
        if (mirror_lon(sat, rangelon, &mlon, satmap->left_side_lon))
            warped = TRUE;

        lonlat_to_xy(satmap, rangelon, rangelat, &sx, &sy);
        lonlat_to_xy(satmap, mlon, rangelat, &msx, &msy);

        points1->coords[2 * azi] = sx;
        points1->coords[2 * azi + 1] = sy;

        /* Add mirrored point */
        points1->coords[718 - 2 * azi] = msx;
        points1->coords[719 - 2 * azi] = msy;
    }

    /* points1 now contains 360 pairs of map-based XY coordinates.
       Check whether actions 1, 2 or 3 have to be performed.
     */

    /* pole is covered => sort points1 and add additional points */
    if (pole_is_covered(sat))
    {

        sort_points_x(satmap, sat, points1, 360);
        numrc = 1;
    }

    /* pole not covered but range circle has been warped
       => split points */
    else if (warped == TRUE)
    {

        lonlat_to_xy(satmap, sat->ssplon, sat->ssplat, &ssx, &ssy);
        split_points(satmap, sat, ssx);
        numrc = 2;

    }
    else
    {
        /* the nominal condition => points1 is adequate */
        numrc = 1;
    }

    return numrc;
}
